import type { Metadata } from "next";
import type { ReactNode } from "react";

import {
  Avatar,
  Button,
  ChartIcon,
  CheckIcon,
  Chip,
  CloseIcon,
  DownloadIcon,
  HeartIcon,
  HomeIcon,
  IconButton,
  PageHeader,
  PauseIcon,
  PlayIcon,
  PlusIcon,
  ProgressBar,
  SearchField,
  SearchIcon,
  SkipIcon,
  Surface,
  SwipeIcon,
  Tag,
  UserIcon,
} from "@/components/ui";

export const metadata: Metadata = {
  title: "UI components · MusicVault",
  robots: { index: false },
};

const ICONS = [
  { name: "home", Icon: HomeIcon },
  { name: "swipe", Icon: SwipeIcon },
  { name: "heart", Icon: HeartIcon },
  { name: "search", Icon: SearchIcon },
  { name: "chart", Icon: ChartIcon },
  { name: "user", Icon: UserIcon },
  { name: "plus", Icon: PlusIcon },
  { name: "check", Icon: CheckIcon },
  { name: "play", Icon: PlayIcon },
  { name: "pause", Icon: PauseIcon },
  { name: "close", Icon: CloseIcon },
  { name: "skip", Icon: SkipIcon },
  { name: "download", Icon: DownloadIcon },
];

type SectionProps = {
  title: string;
  stack?: boolean;
  children: ReactNode;
};

function Section({ title, stack, children }: SectionProps) {
  return (
    <section className="flex flex-col gap-4">
      <h2 className="text-[28px] font-semibold tracking-[-0.015em]">{title}</h2>

      <div
        className={
          stack ? "flex flex-col gap-4" : "flex flex-wrap items-center gap-4"
        }
      >
        {children}
      </div>
    </section>
  );
}

export default function UiGalleryPage() {
  return (
    <>
      <PageHeader
        title="UI components"
        description="Every shared primitive, in each variant and state. Build features out of these, and add a missing variant here rather than restyling a copy in feature code."
        actions={
          <Button variant="secondary" size="sm" href="/dashboard">
            Back to home
          </Button>
        }
      />

      <Section title="Button">
        <Button variant="primary" size="sm">
          Primary sm
        </Button>
        <Button variant="primary" size="md">
          Primary md
        </Button>
        <Button variant="primary" size="lg">
          Primary lg
        </Button>
        <Button variant="secondary" size="sm">
          Secondary sm
        </Button>
        <Button variant="secondary" size="md">
          Secondary md
        </Button>
        <Button variant="secondary" size="lg">
          Secondary lg
        </Button>
        <Button variant="quiet" size="sm">
          Quiet sm
        </Button>
        <Button variant="quiet" size="md">
          Quiet md
        </Button>
        <Button variant="quiet" size="lg">
          Quiet lg
        </Button>
        <Button
          variant="primary"
          size="md"
          icon={<PlusIcon className="h-5 w-5" />}
        >
          With an icon
        </Button>
        <Button variant="secondary" size="md" href="/library">
          Renders a link
        </Button>
      </Section>

      <Section title="IconButton">
        <IconButton size={56} tone="olive" label="Play">
          <PlayIcon className="h-6 w-6" />
        </IconButton>
        <IconButton size={56} tone="blush" label="Pause">
          <PauseIcon className="h-6 w-6" />
        </IconButton>
        <IconButton size={56} tone="paper" label="Skip">
          <SkipIcon className="h-6 w-6" />
        </IconButton>
        <IconButton size={56} tone="green" label="Keep">
          <CheckIcon className="h-6 w-6" />
        </IconButton>
        <IconButton size={48} tone="olive" label="Pass">
          <CloseIcon className="h-5 w-5" />
        </IconButton>
        <IconButton size={76} tone="olive" label="Save to vault">
          <HeartIcon className="h-8 w-8" />
        </IconButton>
      </Section>

      <Section title="Chip">
        <Chip pressed={false}>Not selected</Chip>
        <Chip pressed>Selected</Chip>

        <Surface tone="olive" className="flex flex-wrap items-center gap-4">
          <Chip tone="dark" pressed={false}>
            Dark, not selected
          </Chip>
          <Chip tone="dark" pressed>
            Dark, selected
          </Chip>
        </Surface>
      </Section>

      <Section title="Tag">
        <Tag>Acoustic</Tag>
        <Tag>Indie folk</Tag>

        <Surface tone="olive" className="flex flex-wrap items-center gap-4">
          <Tag tone="dark">Dark on olive</Tag>
        </Surface>
      </Section>

      <Section title="SearchField" stack>
        <SearchField label="Find a song" placeholder="Song or artist" />
        <SearchField
          label="Find a song"
          labelVisible
          placeholder="Song or artist"
        />
      </Section>

      <Section title="Surface" stack>
        <Surface>Paper, the default, 28px padding</Surface>
        <Surface tone="olive">Olive, text turns blush</Surface>
        <Surface tone="orchid">Orchid, for insights</Surface>
        <Surface tone="dashed">Dashed, for coming soon and drop areas</Surface>
        <Surface padding="lg">Paper, 40px padding</Surface>
      </Section>

      <Section title="ProgressBar" stack>
        <ProgressBar value={0} label="Setup progress, nothing done" />
        <ProgressBar value={0.25} label="Setup progress, 1 of 4 done" />
        <ProgressBar value={1} label="Setup progress, done" />
      </Section>

      <Section title="Avatar">
        <Avatar size={32} initial="A" />
        <Avatar size={40} initial="M" />
        <Avatar size={56} initial="R" />
        <Avatar size={40} />
      </Section>

      <Section title="PageHeader" stack>
        <p className="max-w-[60ch] text-[17px]">
          The header at the top of this page is the live example. It takes a
          title, an optional description, and an optional actions slot that
          wraps underneath on phones. Every app page starts with one, and it
          owns the only h1 on the page.
        </p>
      </Section>

      <Section title="icons">
        {ICONS.map(({ name, Icon }) => (
          <span
            key={name}
            className="flex w-16 flex-col items-center gap-2 text-[13px]"
          >
            <Icon className="h-6 w-6" />
            {name}
          </span>
        ))}
      </Section>
    </>
  );
}
