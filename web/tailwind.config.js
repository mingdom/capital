/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./pages/**/*.{js,ts,jsx,tsx,mdx}",
        "./components/**/*.{js,ts,jsx,tsx,mdx}",
        "./app/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    darkMode: "class",
    theme: {
        extend: {
            colors: {
                border: "rgb(from var(--border) r g b / <alpha-value>)",
                input: "rgb(from var(--input) r g b / <alpha-value>)",
                ring: "rgb(from var(--ring) r g b / <alpha-value>)",
                background: "rgb(from var(--background) r g b / <alpha-value>)",
                foreground: "rgb(from var(--foreground) r g b / <alpha-value>)",
                primary: {
                    DEFAULT: "rgb(from var(--primary) r g b / <alpha-value>)",
                    foreground: "rgb(from var(--primary-foreground) r g b / <alpha-value>)",
                },
                secondary: {
                    DEFAULT: "rgb(from var(--secondary) r g b / <alpha-value>)",
                    foreground: "rgb(from var(--secondary-foreground) r g b / <alpha-value>)",
                },
                destructive: {
                    DEFAULT: "rgb(from var(--destructive) r g b / <alpha-value>)",
                    foreground: "rgb(from var(--destructive-foreground) r g b / <alpha-value>)",
                },
                muted: {
                    DEFAULT: "rgb(from var(--muted) r g b / <alpha-value>)",
                    foreground: "rgb(from var(--muted-foreground) r g b / <alpha-value>)",
                },
                accent: {
                    DEFAULT: "rgb(from var(--accent) r g b / <alpha-value>)",
                    foreground: "rgb(from var(--accent-foreground) r g b / <alpha-value>)",
                },
                popover: {
                    DEFAULT: "rgb(from var(--popover) r g b / <alpha-value>)",
                    foreground: "rgb(from var(--popover-foreground) r g b / <alpha-value>)",
                },
                card: {
                    DEFAULT: "rgb(from var(--card) r g b / <alpha-value>)",
                    foreground: "rgb(from var(--card-foreground) r g b / <alpha-value>)",
                },
            },
            borderRadius: {
                lg: "var(--radius)",
                md: "calc(var(--radius) - 2px)",
                sm: "calc(var(--radius) - 4px)",
            },
            fontFamily: {
                sans: ["var(--font-sans)"],
                heading: ["var(--font-heading)"],
                mono: ["var(--font-mono)"],
            },
        },
    },
    plugins: [],
};
