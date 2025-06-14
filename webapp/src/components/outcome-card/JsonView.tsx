"use client";

import ReactJsonView from "react18-json-view";
import "react18-json-view/src/style.css";
import { Outcome } from "@/lib/types";

const JsonView: React.FC<{ outcome: Outcome }> = ({ outcome }) => {
  return <ReactJsonView src={outcome} collapsed={({ depth }) => depth === 1} />;
};

export default JsonView;
