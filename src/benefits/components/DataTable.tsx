import type { ReactNode } from 'react';

export interface Column<T> {
  key: string;
  header: ReactNode;
  render: (row: T) => ReactNode;
  className?: string;
  headerClassName?: string;
}

interface Props<T> {
  columns: Column<T>[];
  rows: T[];
  rowKey: (row: T) => string;
  onRowClick?: (row: T) => void;
  rowClassName?: (row: T) => string;
  emptyText?: string;
  dense?: boolean;
}

/** 通用表格：小螢幕可橫向捲動。 */
export function DataTable<T>({ columns, rows, rowKey, onRowClick, rowClassName, emptyText = '沒有資料', dense = false }: Props<T>) {
  const cell = dense ? 'px-3 py-1.5' : 'px-3 py-2.5';
  return (
    <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-50">
          <tr>
            {columns.map((column) => (
              <th key={column.key} scope="col" className={`${cell} whitespace-nowrap text-left text-xs font-semibold uppercase tracking-wide text-slate-500 ${column.headerClassName ?? ''}`}>
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {rows.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="px-3 py-8 text-center text-sm text-slate-400">
                {emptyText}
              </td>
            </tr>
          ) : (
            rows.map((row) => (
              <tr
                key={rowKey(row)}
                onClick={onRowClick ? () => onRowClick(row) : undefined}
                className={`${onRowClick ? 'cursor-pointer hover:bg-blue-50/60' : ''} ${rowClassName ? rowClassName(row) : ''}`}
              >
                {columns.map((column) => (
                  <td key={column.key} className={`${cell} align-top text-slate-700 ${column.className ?? ''}`}>
                    {column.render(row)}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
