function ThemeToggle({ theme, setTheme }) {
  return (
    <div className="theme-toggle">
      <button
        type="button"
        className={theme === "light" ? "active" : ""}
        onClick={() => setTheme("light")}
      >
        <span aria-hidden="true">☀</span>
        <span>Light</span>
      </button>

      <button
        type="button"
        className={theme === "color" ? "active" : ""}
        onClick={() => setTheme("color")}
      >
        <span aria-hidden="true">◉</span>
        <span>Color</span>
      </button>
    </div>
  );
}

export default ThemeToggle;


