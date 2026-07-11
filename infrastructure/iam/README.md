# Deployer IAM Policies (`hairlyncapp`)

These are the **least-privilege** customer-managed policies for the Terraform
deployer user `hairlyncapp`. They are managed **out-of-band via the AWS CLI**
(not Terraform) on purpose — `hairlyncapp` is the identity Terraform runs as,
so managing its own permissions in Terraform state risks a mid-apply lockout.

| Policy | ARN | Purpose |
|---|---|---|
| `HairIQ-TerraformInfra` | `arn:aws:iam::242969681131:policy/HairIQ-TerraformInfra` | ec2/rds/ecr/s3/dynamodb/kms — region-locked to `eu-north-1` + scoped to our buckets/table/repos |
| `HairIQ-TerraformIAM` | `arn:aws:iam::242969681131:policy/HairIQ-TerraformIAM` | IAM writes scoped to `hairiq-*` roles/instance-profiles/policies + the GitHub OIDC provider; `PassRole` only the EC2 role. Read-only IAM elsewhere. **No privilege escalation.** |

Note the policies are named `HairIQ-*` (capitalized) so they fall **outside** the
`policy/hairiq-*` self-manage scope — `hairlyncapp` cannot widen its own grants;
only an admin/root can edit these (separation of duties).

## Apply / update (run as an admin or root, not as hairlyncapp after hardening)
```bash
# create
aws iam create-policy --policy-name HairIQ-TerraformInfra --policy-document file://HairIQ-TerraformInfra.json
# update (new default version)
aws iam create-policy-version --policy-arn arn:aws:iam::242969681131:policy/HairIQ-TerraformInfra \
  --policy-document file://HairIQ-TerraformInfra.json --set-as-default
```

## Rollback (re-grant broad access if ever locked out)
```bash
for p in IAMFullAccess AmazonEC2FullAccess AmazonRDSFullAccess AmazonS3FullAccess \
         AmazonDynamoDBFullAccess AmazonEC2ContainerRegistryFullAccess; do
  aws iam attach-user-policy --user-name hairlyncapp --policy-arn arn:aws:iam::aws:policy/$p
done
```
Root account is the ultimate break-glass (console).

## GitHub Actions ECR access (`hairiq-github-ci`)

Attach or inline `github-actions-ecr-policy.json` on the GitHub OIDC role:

`arn:aws:iam::242969681131:role/hairiq-github-ci`

This policy supports the ECR steps in `.github/workflows/deploy.yml`:

- `aws-actions/amazon-ecr-login` requires `ecr:GetAuthorizationToken`.
- `Validate ECR repositories` requires `ecr:DescribeRepositories`.
- `docker/build-push-action` with `push: true` requires the repository-scoped layer upload and image push actions.

`ecr:GetAuthorizationToken` must use `"Resource": "*"` because AWS does not
support resource-level scoping for that action. All other ECR permissions are
scoped to the four existing repositories in account `242969681131`, region
`eu-north-1`.

The GitHub repository identity for OIDC trust is `Md-Fahad-Mir/HairLync`.
Existing AWS resources may still use the `hairiq-*` names.
