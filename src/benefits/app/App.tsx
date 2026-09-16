import Link from "next/link";
import { NavLink, Outlet } from 'react-router-dom';
import { DISCLAIMER } from '../utils/labels';

const navClass = ({ isActive }: { isActive: boolean }) =>
  `rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${isActive ? 'bg-slate-900 text-white' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'}`;

export default function App() {
  return (
    <div className="flex min-h-screen flex-col bg-slate-50 text-slate-900">
      <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/95 backdrop-blur">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3 px-4 py-3 sm:px-6">
          <NavLink to="/data-center" className="flex items-center gap-2">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 text-sm font-bold text-white">補</span>
            <span className="leading-tight">
              <span className="block text-sm font-semibold text-slate-900">官方補助 智能搜尋與資格媒合平台</span>
              <span className="block text-[11px] text-slate-500">資料皆來自政府與學校官方網站公告，每筆保留原文與來源</span>
            </span>
          </NavLink>
          <nav className="flex flex-wrap items-center gap-1" aria-label="主選單"><Link href="/" className="rounded-md px-3 py-1.5 text-sm text-brand-600">使用者介面</Link><a href="/admin" className="rounded-md px-3 py-1.5 text-sm text-brand-600">需求管理</a>
            <NavLink to="/data-center" className={navClass}>
              資料中心
            </NavLink>
            <NavLink to="/registry" className={navClass}>
              屬性登錄表與類別
            </NavLink>
          </nav>
        </div>
      </header>

      <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-6 sm:px-6">
        <Outlet />
      </main>

      <footer className="border-t border-slate-200 bg-white">
        <div className="mx-auto max-w-7xl space-y-1 px-4 py-4 text-xs text-slate-500 sm:px-6">
          <p className="font-medium text-slate-600">{DISCLAIMER}</p>
          <p>本平台僅彙整官方公開資訊，不代表任何主辦機關；申請文件與期限請以官方公告為準。</p>
        </div>
      </footer>
    </div>
  );
}
