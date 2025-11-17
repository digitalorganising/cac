import React from "react";

const WigglyBarChart = React.forwardRef<
  SVGSVGElement,
  React.SVGProps<SVGSVGElement>
>((props, forwardedRef) => {
  return (
    <svg
      width="15"
      height="15"
      viewBox="0 0 15 15"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      {...props}
      ref={forwardedRef}
    >
      <rect
        className="origin-bottom group-hover:[animation:wiggle_0.4s_linear]"
        x="1"
        y="5.5"
        width="1"
        height="8"
        fill="currentColor"
      />
      <rect
        className="origin-bottom group-hover:[animation:wiggle_0.6s_linear]"
        x="3"
        y="7.5"
        width="1"
        height="6"
        fill="currentColor"
      />
      <rect
        className="origin-bottom group-hover:[animation:wiggle_0.5s_linear]"
        x="5"
        y="4.5"
        width="1"
        height="9"
        fill="currentColor"
      />
      <rect
        className="origin-bottom group-hover:[animation:wiggle_0.7s_linear]"
        x="7"
        y="5.5"
        width="1"
        height="8"
        fill="currentColor"
      />
      <rect
        className="origin-bottom group-hover:[animation:wiggle_0.4s_linear]"
        x="9"
        y="3.5"
        width="1"
        height="10"
        fill="currentColor"
      />
      <rect
        className="origin-bottom group-hover:[animation:wiggle_0.7s_linear]"
        x="11"
        y="1.5"
        width="1"
        height="12"
        fill="currentColor"
      />
      <rect
        className="origin-bottom group-hover:[animation:wiggle_0.7s_linear]"
        x="13"
        y="3.5"
        width="1"
        height="10"
        fill="currentColor"
      />
    </svg>
  );
});

WigglyBarChart.displayName = "WigglyBarChart";

export default WigglyBarChart;
