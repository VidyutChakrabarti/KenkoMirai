import Link from "next/link";
import { useRouter } from "next/router";

const links = [
  { href: "/", label: "Overview" },
  { href: "/simulation", label: "Scenario lab" },
  { href: "/dashboard", label: "Operations" },
];

export default function Header() {
  const router = useRouter();
  return (
    <header className="site-header">
      <div className="header-inner">
        <Link className="brand" href="/" aria-label="KenkoMirai home">
          <span className="brand-mark" aria-hidden="true">K</span>
          <span><strong>KenkoMirai</strong><small>Urban health scenarios</small></span>
        </Link>
        <nav className="site-nav" aria-label="Primary navigation">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={router.pathname === link.href ? "active" : undefined}
              aria-current={router.pathname === link.href ? "page" : undefined}
            >
              {link.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
