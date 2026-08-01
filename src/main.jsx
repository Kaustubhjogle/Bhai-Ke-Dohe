import { useCallback, useDeferredValue, useEffect, useMemo, useState } from "react";
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
  const [page, setPage] = useState(1);
  const deferredQuery = useDeferredValue(query);

  const filteredPosts = useMemo(() => {
    const normalizedQuery = deferredQuery.trim().toLowerCase();
    return POSTS.filter(
      (post) =>
        (filter === "all" || post.tag === filter) &&
        post.text.toLowerCase().includes(normalizedQuery),
    );
  }, [deferredQuery, filter]);

  const totalPages = Math.max(1, Math.ceil(filteredPosts.length / 4));
  const currentPage = Math.min(page, totalPages);
  const visiblePosts = useMemo(() => {
    const start = (currentPage - 1) * 4;
    return filteredPosts.slice(start, start + 4);
  }, [filteredPosts, currentPage]);

  const showNextPost = useCallback(() => {
    setFeaturedIndex((currentIndex) => (currentIndex + 1) % POSTS.length);
  }, []);

  const resetArchive = useCallback(() => {
    setFilter("all");
    setQuery("");
    setPage(1);
  }, []);

  useEffect(() => {
    setPage(1);
  }, [filter, query]);

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
        posts={visiblePosts}
        filter={filter}
        query={query}
        page={currentPage}
        totalPages={totalPages}
        onFilterChange={(nextFilter) => {
          setFilter(nextFilter);
          setPage(1);
        }}
        onQueryChange={(nextQuery) => {
          setQuery(nextQuery);
          setPage(1);
        }}
        onReset={resetArchive}
        onPageChange={setPage}
      />
      <SiteFooter />
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
