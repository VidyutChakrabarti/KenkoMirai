import Link from 'next/link';

export default function Header() {
    return (
        <header style={{ background: '#f0f0f0', padding: '1rem' }}>
            <nav>
                <Link href="/">Home</Link> |{" "}
                <Link href="/simulation">Simulation</Link> |{" "}
                <Link href="/dashboard">Dashboard</Link>
            </nav>
        </header>
    );
}
