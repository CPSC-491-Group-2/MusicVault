import type { Metadata } from "next";
import type { ReactNode } from "react";

import { AccountDetailsPanel } from "@/components/account/AccountDetailsPanel";
import { PasswordPanel } from "@/components/account/PasswordPanel";
import { SpotifyConnectionPanel } from "@/components/account/SpotifyConnectionPanel";
import { authErrorMessage } from "@/components/auth/authErrors";
import { LoginPanel } from "@/components/auth/LoginPanel";
import { SignupPanel } from "@/components/auth/SignupPanel";
import { AccountChip } from "@/components/shell/AccountChip";
import {
  Avatar,
  Button,
  ChartIcon,
  CheckIcon,
  Chip,
  CloseIcon,
  DownloadIcon,
  FormMessage,
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
  TextField,
  UserIcon,
} from "@/components/ui";
import type { User } from "@/types/api";

export const metadata: Metadata = {
  title: "UI components · MusicVault",
  robots: { index: false },
};

const SPOTIFY_USER: User = {
  id: "u1",
  email: "anjelo@example.com",
  display_name: "Anjelo",
  has_password: true,
  spotify: { connected: true, display_name: "anjelo" },
  created_at: "2026-10-04T18:22:00Z",
  updated_at: "2026-10-20T09:15:00Z",
};

const LOCAL_USER: User = {
  id: "u2",
  email: "maya.chen@example.com",
  display_name: "Maya Chen",
  has_password: true,
  spotify: { connected: false, display_name: null },
  created_at: "2026-09-14T16:05:00Z",
  updated_at: "2026-10-11T12:40:00Z",
};

const SPOTIFY_ONLY_USER: User = {
  id: "u3",
  email: null,
  display_name: "Jordan",
  has_password: false,
  spotify: { connected: true, display_name: "jordanplays" },
  created_at: "2026-10-19T21:30:00Z",
  updated_at: "2026-10-19T21:30:00Z",
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
        <Button variant="primary" size="md" disabled>
          Primary disabled
        </Button>
        <Button variant="secondary" size="md" disabled>
          Secondary disabled
        </Button>
        <Button variant="quiet" size="md" disabled>
          Quiet disabled
        </Button>
        <Button variant="primary" size="md" type="submit">
          Submits a form
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

      <Section title="TextField" stack>
        <TextField label="Email" type="email" />
        <TextField label="Name" hint="Shown on your profile" />
        <TextField label="Email" type="email" error="Enter your email" />
        <TextField
          label="Password"
          type="password"
          hint="8 to 128 characters"
        />
        <TextField
          label="Email"
          type="email"
          defaultValue="anjelo@example.com"
          disabled
        />
      </Section>

      <Section title="FormMessage" stack>
        <FormMessage tone="error">
          {authErrorMessage("invalid_credentials")}
        </FormMessage>
        <FormMessage tone="success">Password saved</FormMessage>
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

      <Section title="Auth" stack>
        <div className="flex flex-wrap items-start gap-6">
          <LoginPanel titleAs="h2" />
          <LoginPanel titleAs="h2" error="spotify_not_allowed" />
          <LoginPanel titleAs="h2" pending />
          <SignupPanel titleAs="h2" />
          <SignupPanel titleAs="h2" error="email_taken" />
        </div>
      </Section>

      <Section title="Account" stack>
        <div className="flex flex-wrap items-start gap-4">
          <AccountChip user={SPOTIFY_USER} className="w-[220px]" />
          <AccountChip user={LOCAL_USER} className="w-[220px]" />
          <AccountChip user={SPOTIFY_ONLY_USER} className="w-[220px]" />
        </div>
        <div className="grid items-start gap-6 min-[1200px]:grid-cols-2">
          <SpotifyConnectionPanel user={SPOTIFY_USER} />
          <SpotifyConnectionPanel user={SPOTIFY_ONLY_USER} />
          <SpotifyConnectionPanel user={LOCAL_USER} />
          <SpotifyConnectionPanel user={LOCAL_USER} error="spotify_in_use" />
          <SpotifyConnectionPanel user={SPOTIFY_USER} justConnected />
          <PasswordPanel user={LOCAL_USER} />
          <PasswordPanel user={SPOTIFY_ONLY_USER} />
          <AccountDetailsPanel user={LOCAL_USER} />
          <AccountDetailsPanel user={SPOTIFY_ONLY_USER} />
        </div>
      </Section>
    </>
  );
}
