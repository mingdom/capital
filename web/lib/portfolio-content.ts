import fs from "fs";
import path from "path";
import matter from "gray-matter";
import { remark } from "remark";
import html from "remark-html";

const contentDirectory = path.join(process.cwd(), "content/portfolio");

export interface PortfolioSection {
    id: string;
    title: string;
    order: number;
    icon: string;
    accent: string;
    contentHtml: string;
}

/**
 * Loads all portfolio sections from the /content/portfolio directory.
 * Parses markdown and returns structured content with HTML.
 */
export async function getPortfolioSections(): Promise<PortfolioSection[]> {
    // Check if directory exists
    if (!fs.existsSync(contentDirectory)) {
        console.error(`Content directory not found: ${contentDirectory}`);
        return [];
    }

    const fileNames = fs.readdirSync(contentDirectory);
    const allSectionsData = await Promise.all(
        fileNames
            .filter((fileName) => fileName.endsWith(".md"))
            .map(async (fileName) => {
                const id = fileName.replace(/\.md$/, "");
                const fullPath = path.join(contentDirectory, fileName);

                try {
                    const fileContents = fs.readFileSync(fullPath, "utf8");

                    // Use gray-matter to parse the post metadata section
                    const matterResult = matter(fileContents);

                    // Use remark to convert markdown into HTML string
                    const processedContent = await remark()
                        .use(html)
                        .process(matterResult.content);
                    const contentHtml = processedContent.toString();

                    // Combine the data with the id and contentHtml
                    return {
                        id,
                        contentHtml,
                        title: matterResult.data.title || id,
                        order: matterResult.data.order || 99,
                        icon: matterResult.data.icon || "Info",
                        accent: matterResult.data.accent || "purple",
                    } as PortfolioSection;
                } catch (err) {
                    console.error(`Error parsing markdown file ${fileName}:`, err);
                    return {
                        id,
                        contentHtml: `<p class="text-destructive">Error loading content for this section.</p>`,
                        title: id,
                        order: 99,
                        icon: "AlertTriangle",
                        accent: "red",
                    } as PortfolioSection;
                }
            })
    );

    // Sort sections by order
    return allSectionsData.sort((a, b) => a.order - b.order);
}
