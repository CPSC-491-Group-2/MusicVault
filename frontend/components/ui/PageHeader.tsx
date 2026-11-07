import type { ReactNode } from "react";

type PageHeaderProps = {
  title: string;
  description?: string;
  actions?: ReactNode;
};

export function PageHeader({ title, description, actions }: PageHeaderProps) {
  return (
    <header className="flex flex-wrap items-start justify-between gap-x-8 gap-y-6">
      <div className="min-w-0">
        <h1 className="text-balance text-[32px] font-semibold leading-[1.05] tracking-[-0.03em] min-[860px]:text-[44px]">
          {title}
        </h1>

        {description ? (
          <p className="mt-4 max-w-[60ch] text-[18px] leading-[1.5] text-olive/70">
            {description}
          </p>
        ) : null}
      </div>

      {actions ? (
        <div className="flex flex-wrap items-center gap-3">{actions}</div>
      ) : null}
    </header>
  );
}
