"use client";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import App from "@/benefits/app/App";
import BenefitDetailPage from "@/benefits/app/BenefitDetailPage";
import DataCenterPage from "@/benefits/app/DataCenterPage";
import MyBenefitsPage from "@/benefits/app/MyBenefitsPage";
import RegistryPage from "@/benefits/app/RegistryPage";
export default function BenefitsRouter() {
 return <BrowserRouter><Routes><Route element={<App />}>
 <Route path="/data-center" element={<DataCenterPage />} />
 <Route path="/data-center/:id" element={<BenefitDetailPage />} />
 <Route path="/registry" element={<RegistryPage />} />
 <Route path="/my-benefits" element={<MyBenefitsPage />} />
 <Route path="/my-scholarships" element={<Navigate to="/my-benefits" replace />} />
 </Route></Routes></BrowserRouter>;
}
