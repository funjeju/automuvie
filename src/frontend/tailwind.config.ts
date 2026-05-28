import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#090B1A",
        card: "#11142B",
        primary: "#B14CFF",
        "primary-2": "#8A4DFF",
        "primary-3": "#D946EF",
        border: "rgba(255,255,255,0.08)",
        success: "#4ADE80",
        error: "#FF5C7A",
        warning: "#FFC857",
        muted: "rgba(255,255,255,0.7)",
      },
      borderRadius: {
        card: "18px",
        chip: "12px",
      },
      boxShadow: {
        glow: "0 0 24px rgba(177,76,255,0.35)",
        soft: "0 12px 40px -16px rgba(0,0,0,0.7)",
      },
      backgroundImage: {
        "brand-gradient": "linear-gradient(135deg,#8A4DFF 0%,#D946EF 100%)",
        "panel-gradient": "radial-gradient(circle at top, rgba(177,76,255,0.18) 0%, transparent 60%)",
      },
      fontFamily: {
        sans: [
          "Pretendard",
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "sans-serif",
        ],
      },
    },
  },
  plugins: [],
};

export default config;
