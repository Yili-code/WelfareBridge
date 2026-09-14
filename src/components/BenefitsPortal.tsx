"use client";
import dynamic from "next/dynamic";
const Portal = dynamic(() => import("./BenefitsRouter"), { ssr: false, loading: () => <p className="p-8" role="status">正在載入補助資料…</p> });
export default function BenefitsPortal() { return <Portal />; }
