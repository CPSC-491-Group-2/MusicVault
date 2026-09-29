import Link from "next/link";

export default function Navbar() {
  return (
    <nav>
      <Link href="/">Home</Link>
      {" | "}
      <Link href="/library">Library</Link>
      {" | "}
      <Link href="/search">Search</Link>
      {" | "}
      <Link href="/profile">Profile</Link>
    </nav>
  );
}