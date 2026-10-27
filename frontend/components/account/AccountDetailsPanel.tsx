import { Surface } from "@/components/ui/Surface";
import type { User } from "@/types/api";

type AccountDetailsPanelProps = {
  user: User;
  className?: string;
};

const MEMBER_SINCE_FORMAT = new Intl.DateTimeFormat("en-US", {
  month: "short",
  year: "numeric",
  timeZone: "UTC",
});

export function AccountDetailsPanel({
  user,
  className,
}: AccountDetailsPanelProps) {
  const rows = [
    { label: "Name", value: user.display_name },
    { label: "Email", value: user.email },
    {
      label: "Member since",
      value: MEMBER_SINCE_FORMAT.format(new Date(user.created_at)),
    },
  ];

  return (
    <Surface
      className={["flex flex-col gap-5", className].filter(Boolean).join(" ")}
    >
      <h2 className="text-balance text-[28px] font-semibold leading-[1.15] tracking-[-0.015em]">
        Account
      </h2>
      <dl className="flex flex-col gap-5">
        {rows.map(({ label, value }) => (
          <div key={label} className="flex flex-col gap-1">
            <dt className="text-[15px] leading-[1.45] text-olive/70">
              {label}
            </dt>
            <dd
              className={
                value
                  ? "break-words text-[17px] leading-[1.5]"
                  : "text-[17px] leading-[1.5] text-olive/45"
              }
            >
              {value || "Not added yet"}
            </dd>
          </div>
        ))}
      </dl>
    </Surface>
  );
}
