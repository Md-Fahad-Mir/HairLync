<div className="absolute inset-0 z-0 pointer-events-none opacity-[0.22]">
  <svg width="100%" height="100%">
    {/* Lines */}
    {mesh.connections.map(([a, b], i) => {
      const p1 = getPoint(a);
      const p2 = getPoint(b);
      if (!p1 || !p2) return null;

      return (
        <line
          key={i}
          x1={p1.x}
          y1={p1.y}
          x2={p2.x}
          y2={p2.y}
          stroke="rgba(110,231,255,0.6)"
          strokeWidth="0.6"
        />
      );
    })}

    {/* Points */}
    {animatedPoints.map((p, i) => (
      <circle key={i} cx={p.x} cy={p.y} r="1.4" fill="rgba(110,231,255,0.8)" />
    ))}
  </svg>

  {/* 🔥 soft fade (light, not strong) */}
  <div className="absolute inset-0 bg-gradient-to-b from-white/60 via-transparent to-white/60" />
</div>;
