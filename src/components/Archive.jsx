import { memo } from "react";
import { FILTERS } from "../data/posts";
import { ProfileIdentity } from "./ProfileIdentity";

const TweetCard = memo(function TweetCard({ post, index }) {
  const id = String(index + 1).padStart(2, "0");
  return (
    <article
      className={`entry${post.highlight ? " entry--highlight" : ""}`}
      style={{ "--entry": index }}
    >
      <div className="quote-layer" aria-hidden="true">
        {post.text}
      </div>
      {post.date && <div className="date-layer">{post.date}</div>}
      <div className="post-card">
        <div className="post-topline">
          <span>ARCHIVE / {id}</span>
          <span>{post.tag}</span>
        </div>
        <ProfileIdentity showMark />
        <p>{post.text}</p>
        <div className="post-footer">
          {post.date && <time>{post.date}</time>}
          <a
            href="https://x.com/BeingSalmanKhan"
            target="_blank"
            rel="noreferrer"
          >
            View on X <span>↗</span>
          </a>
        </div>
      </div>
    </article>
  );
});

export const Archive = memo(function Archive({
  posts,
  filter,
  query,
  onFilterChange,
  onQueryChange,
  onReset,
}) {
  return (
    <section className="archive" id="archive">
      <header className="archive-head">
        <div>
          <p className="eyebrow">THE COLLECTION</p>
          <h2>
            Unforgettable
            <br />
            thoughts.
          </h2>
        </div>
        <p className="archive-note">
          No trailers. No launches. No promotion.
          <br />
          Just the tweets that stayed with us.
        </p>
      </header>
      <div className="controls">
        <div className="filter-row">
          {FILTERS.map((item) => (
            <button
              key={item}
              className={filter === item ? "active" : ""}
              onClick={() => onFilterChange(item)}
            >
              {item === "all" ? "Everything" : item}
            </button>
          ))}
        </div>
        <label className="search">
          <span>⌕</span>
          <input
            aria-label="Search the archive"
            value={query}
            onChange={(event) => onQueryChange(event.target.value)}
            placeholder="Search a thought"
          />
        </label>
      </div>
      <div className="entries">
        {posts.length ? (
          posts.map((post, index) => (
            <TweetCard key={post.id} post={post} index={index} />
          ))
        ) : (
          <div className="empty">
            <p>No thought found.</p>
            <button onClick={onReset}>Reset archive</button>
          </div>
        )}
      </div>
    </section>
  );
});
