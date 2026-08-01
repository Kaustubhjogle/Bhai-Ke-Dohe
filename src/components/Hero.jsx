import { memo } from "react";
import { formatTimestamp, getQuoteLength } from "../data/posts";
import { Mark } from "./Mark";
import { ProfileIdentity } from "./ProfileIdentity";

export const Hero = memo(function Hero({ post, index, total, onNext }) {
  const id = String(index + 1).padStart(2, "0");
  const timestamp = formatTimestamp(post.date);
  const quoteLength = getQuoteLength(post.text);

  return (
    <section className="hero" id="top" aria-label="Featured tweet">
      <div className="hero-kicker">
        <p className="eyebrow">FEATURED THOUGHT / {id}</p>
        <span>
          {index + 1} / {total}
        </span>
      </div>
      <div className="hero-stage">
        <div className="featured-post-stack">
          <div className={`hero-quote hero-quote--${quoteLength}`}>
            “{post.text}”
          </div>
          <article className="hero-window">
            <div className="hero-post-actions">
              <a
                href="https://x.com/BeingSalmanKhan"
                target="_blank"
                rel="noreferrer"
                className="hero-x-button"
              >
                <Mark /> <span>.com</span>
              </a>
              <span className="more-options" aria-hidden="true">
                •••
              </span>
            </div>
            <div className="window-content">
              <ProfileIdentity hero />
              <p>{post.text}</p>
              {timestamp && (
                <div className="post-footer hero-post-footer">
                  <time>{timestamp}</time>
                </div>
              )}
            </div>
          </article>
        </div>
      </div>
      <div className="hero-actions">
        <a href="#archive" className="archive-link">
          BROWSE THE COLLECTION <span>↓</span>
        </a>
        <button className="next-thought" onClick={onNext}>
          <span>NEXT THOUGHT</span>
          <b>→</b>
        </button>
      </div>
    </section>
  );
});
