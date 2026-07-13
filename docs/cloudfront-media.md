# CloudFront CDN for S3 Media

CloudFront sits in front of the existing S3 media bucket (`hairiq-media-prod`)
so uploaded **media** is cached at edge locations and served over a stable
HTTPS domain. Only the `media/` prefix is fronted — Django **static** files are
served by WhiteNoise from the container, not from S3, and are unaffected.

## Design

- **Access model:** the S3 bucket stays **public** (its bucket policy is
  unchanged). CloudFront uses the bucket's regional REST endpoint as a plain
  custom origin (no Origin Access Control). The existing direct-S3 media URLs
  keep working, so enabling the CDN is a safe, reversible cutover.
- **Domain:** the default `*.cloudfront.net` domain (no ACM cert / Route 53).
- **Caching:** AWS-managed `CachingOptimized` policy (long TTLs, gzip/brotli).
  Media keys are effectively immutable (`AWS_S3_FILE_OVERWRITE=False` means a
  changed file gets a new key), so long edge caching is safe.
- **CORS:** managed CORS-S3 origin-request + CORS response-headers policies,
  matching the bucket's existing CORS config, so cross-origin image loads from
  the web/admin apps succeed.

Terraform: [`infrastructure/terraform/shared/cloudfront.tf`](../infrastructure/terraform/shared/cloudfront.tf).

## How Django uses it

No Django code changes. `services/backend/core/settings.py` already honors
`AWS_S3_CUSTOM_DOMAIN`: when set, both `MEDIA_URL` and every stored file's
`.url()` (via django-storages) are built on that domain. Empty → direct S3.

## Rollout (safe, staged)

> **Prerequisites — run once, by an admin/root, before the first apply:**
>
> 1. **Grant the Terraform deployer CloudFront access.** The `HairIQ-TerraformInfra`
>    policy did not include CloudFront; the grant has been added to
>    [`infrastructure/iam/HairIQ-TerraformInfra.json`](../infrastructure/iam/HairIQ-TerraformInfra.json)
>    (global, **not** region-locked — CloudFront is a global service). Push it to AWS:
>    ```bash
>    cd infrastructure/iam
>    aws iam create-policy-version \
>      --policy-arn arn:aws:iam::242969681131:policy/HairIQ-TerraformInfra \
>      --policy-document file://HairIQ-TerraformInfra.json --set-as-default
>    ```
>    Without this, `terraform plan`/`apply` fails with `AccessDenied` on
>    `cloudfront:ListCachePolicies` (the managed-policy data sources).
>
> 2. **Review pre-existing state drift first.** A `terraform plan` in this
>    environment currently shows in-place updates to the EIP, S3 CORS config,
>    and security group, plus a new `aws_iam_role_policy.ec2_s3_media` — all
>    **unrelated to CloudFront** (state has drifted from the committed config).
>    The CloudFront change itself is purely additive (one distribution + three
>    read-only data sources + two outputs; it modifies no existing resource).
>    Run `terraform plan` with the **real** `terraform.tfvars` and confirm the
>    only *new* resource you intend to create is `aws_cloudfront_distribution.media`;
>    decide separately whether to apply the unrelated drift in the same run.

1. **Apply Terraform** (creates the distribution; changes nothing on S3 or the
   running app):
   ```bash
   make tf-apply ENV=production      # or: cd infrastructure/terraform/environments/production && terraform apply
   ```
   A new distribution takes ~5–15 min to deploy globally.
2. **Get the domain:**
   ```bash
   cd infrastructure/terraform/environments/production
   terraform output -raw cloudfront_domain_name    # e.g. d1234abcd.cloudfront.net
   ```
3. **Smoke-test the CDN before switching Django to it.** Pick any existing key
   and confirm it serves through CloudFront:
   ```bash
   curl -I "https://<cloudfront-domain>/media/<some-existing-key>"
   # Expect: HTTP/2 200 and an `x-cache: Hit/Miss from cloudfront` header
   ```
4. **Point Django at the CDN:** set `AWS_S3_CUSTOM_DOMAIN=<cloudfront-domain>`
   (no scheme, no path) in the production backend env
   (`deployment/environments/.env.production.backend`), then redeploy the
   backend (push to `main`, or `make ansible-prod` to re-sync env). New media
   URLs in API responses will be CloudFront URLs; old direct-S3 URLs still work.

## Post-cutover verification

After setting `AWS_S3_CUSTOM_DOMAIN` and redeploying the backend:

1. **API media URLs use CloudFront.** Hit an endpoint that returns an image
   (e.g. a barber profile with an avatar) and confirm the URL host is the
   CloudFront domain:
   ```bash
   curl -s https://api.hairlync.com/api/<some-profile-endpoint>/ \
     | grep -oE 'https://[^"]+/media/[^"]+' | head
   # Expect: https://<cloudfront-domain>/media/...
   ```
2. **Uploads still land in S3.** Upload an image through the app/admin, then:
   ```bash
   aws s3 ls "s3://hairiq-media-prod/media/" --recursive | tail
   # The new object appears under the S3 bucket (CloudFront only fronts reads).
   ```
   Its API URL is served via CloudFront; the object itself lives in S3.
3. **Existing direct S3 URLs still work** (bucket stays public):
   ```bash
   curl -I "https://hairiq-media-prod.s3.eu-north-1.amazonaws.com/media/<existing-key>"
   # Expect: HTTP 200 — old links in existing data are not broken.
   ```

## Rollback

- **Instant, no infra change:** clear `AWS_S3_CUSTOM_DOMAIN` (set it empty) in
  the backend env and redeploy. Django immediately reverts to direct S3 URLs.
  The distribution can stay in place, unused.
- **Remove the CDN entirely:** revert the Terraform change and `terraform
  apply` (deletes the distribution). Because the bucket was never locked to
  CloudFront, nothing else needs to change.

## Cache invalidation

Media keys are immutable, so invalidation is rarely needed. If you must purge:
```bash
DIST=$(cd infrastructure/terraform/environments/production && terraform output -raw cloudfront_distribution_id)
aws cloudfront create-invalidation --distribution-id "$DIST" --paths '/media/*'
```

## Notes

- Existing `hairiq-*` resource names are unchanged.
- Static files are **not** on CloudFront (WhiteNoise serves them); this is
  intentional and matches the current architecture.
- To later harden to a private, CloudFront-only bucket (OAC), switch the origin
  to an `aws_cloudfront_origin_access_control` and restrict the bucket policy to
  the distribution — a separate, deliberate change (direct S3 URLs would then
  stop working).
