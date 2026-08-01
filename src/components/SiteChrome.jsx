import { memo } from "react";

export const SiteHeader = memo(function SiteHeader() {
  return (
    <nav>
      <a className="wordmark" href="#top">
        𝗕𝗛𝗔𝗜 𝗞𝗘 𝗗𝗢𝗛𝗘
      </a>
      <div className="nav-meta">
        <p className="footer-credit">
          <a
            href="https://github.com/Kaustubhjogle"
            target="_blank"
            rel="noreferrer"
            >
            Kaustubh Jogle
          </a>
        </p>
        <span>THE UNOFFICIAL ARCHIVE</span>
        <a
          href="https://x.com/BeingSalmanKhan"
          target="_blank"
          rel="noreferrer"
        >
          @BEINGSALMANKHAN <span>↗</span>
        </a>
      </div>
    </nav>
  );
});

export const SiteFooter = memo(function SiteFooter() {
  return (
    <footer>
      <div className="footer-note">
        <p>
          Welcome to 𝗕𝗛𝗔𝗜 𝗞𝗘 𝗗𝗢𝗛𝗘. Because someone had to archive the greatest,
          most out-of-context thoughts in internet history. Bhai blessed the
          timeline with random life lessons and tweets so cryptic they belong in
          a museum. The unfiltered mind of a legend.
        </p>
        <p>
          Disclaimer: Bhai Ke Dohe is an unofficial fan-made site. It is not
          affiliated with, endorsed by, or associated with Salman Khan, Being
          Human, or their representatives.
        </p>
        <p className="footer-credit">
          Github: Kaustubh Jogle
          <a
            href="https://github.com/Kaustubhjogle"
            target="_blank"
            rel="noreferrer"
          >
            <span>↗</span>
          </a>
        </p>
        <p className="footer-credit">
          Inspired by @theriyalstore
          <a
            href="https://www.instagram.com/theriyalstore"
            target="_blank"
            rel="noreferrer"
          >
            <span>↗</span>
          </a>
        </p>
      </div>
      <span>AN UNOFFICIAL EDUCATIONAL ARCHIVE</span>
      <span>CURATED WITH RESPECT</span>
      <span>© {new Date().getFullYear()}</span>
    </footer>
  );
});
