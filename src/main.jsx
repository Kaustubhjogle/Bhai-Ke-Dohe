import { useCallback, useDeferredValue, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { Archive } from "./components/Archive";
import { Hero } from "./components/Hero";
import { SiteFooter, SiteHeader } from "./components/SiteChrome";
import { POSTS } from "./data/posts";
import "./styles.css";

function App() {
  const [filter, setFilter] = useState("all");
  const [query, setQuery] = useState("");
  const [featuredIndex, setFeaturedIndex] = useState(0);
  const deferredQuery = useDeferredValue(query);

  const filteredPosts = useMemo(() => {
    const normalizedQuery = deferredQuery.trim().toLowerCase();
    return POSTS.filter(
      (post) =>
        (filter === "all" || post.tag === filter) &&
        post.text.toLowerCase().includes(normalizedQuery),
    );
  }, [deferredQuery, filter]);

  const showNextPost = useCallback(() => {
    setFeaturedIndex((currentIndex) => (currentIndex + 1) % POSTS.length);
  }, []);

  const resetArchive = useCallback(() => {
    setFilter("all");
    setQuery("");
  }, []);

  if (!POSTS.length)
    return (
      <main className="empty-app">No posts are available in the archive.</main>
    );

  return (
    <main>
      <div className="cosmos" aria-hidden="true">
        <span />
        <span />
        <span />
      </div>
      <SiteHeader />
      <Hero
        post={POSTS[featuredIndex]}
        index={featuredIndex}
        total={POSTS.length}
        onNext={showNextPost}
      />
      <Archive
        posts={filteredPosts}
        filter={filter}
        query={query}
        onFilterChange={setFilter}
        onQueryChange={setQuery}
        onReset={resetArchive}
      />
      <SiteFooter />
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
