import Link from "next/link";
import {GenerateForm} from "../components/generate-form";

export default function Home() {
  return (
    <main className="home-shell" id="main-content">
      <header className="site-header">
        <Link className="wordmark" href="/">focusly</Link>
        <Link className="header-action" href="/dashboard">My lessons</Link>
      </header>
      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">Learn in smaller pieces</p>
          <h1>Make the hard part <span>click.</span></h1>
          <p className="lede">
            Turn any topic into a short animated lesson with clear steps,
            captions, and one useful memory check.
          </p>
          <div className="focus-note" aria-label="Lesson format">
            <strong>Built for short focus windows</strong>
            <span>1-2 minute lessons</span>
            <span>Captions on</span>
            <span>One concept at a time</span>
          </div>
        </div>
        <div className="form-stage">
          <span className="form-stage-label">Start here</span>
          <GenerateForm />
        </div>
      </section>
    </main>
  );
}
