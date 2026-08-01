import { memo } from "react";

export const SiteHeader = memo(function SiteHeader() {
  return (
    <nav>
      <a className="wordmark" href="#top">
        𝗕𝗛𝗔𝗜 𝗞𝗘 𝗗𝗢𝗛𝗘
      </a>
      <div className="nav-meta">
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
      <span>AN UNOFFICIAL EDUCATIONAL ARCHIVE</span>
      <span>CURATED WITH RESPECT</span>
      <span>© {new Date().getFullYear()}</span>
    </footer>
  );
});
