"use client";

import ReactJsonView from "react18-json-view";
import { Outcome } from "@/lib/types";

import "react18-json-view/src/style.css";

const JsonView: React.FC<{ outcome: Outcome }> = ({ outcome }) => {
  return <ReactJsonView src={outcome} collapsed={({ depth }) => depth === 1} />;
};

export default JsonView;
