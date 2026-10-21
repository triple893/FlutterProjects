export function formatDate(date: Date | null | undefined): string {
	if (!date) return "";
	const y = date.getFullYear();
	const m = String(date.getMonth() + 1).padStart(2, "0");
	const d = String(date.getDate()).padStart(2, "0");
	return `${y}.${m}.${d}`;
}

/** Sort entries by their `sort_order` field, falling back to the end of the list. */
export function bySortOrder<T extends { data: { sort_order?: number | null } }>(a: T, b: T): number {
	return (a.data.sort_order ?? 1000) - (b.data.sort_order ?? 1000);
}

const NUMERALS = ["壱", "弐", "参", "肆", "伍", "陸", "漆", "捌", "玖", "拾"];

/** Gate number in formal kanji (壱, 弐, 参…), from a zero-based position. */
export function gateNumeral(index: number): string {
	return NUMERALS[index] ?? String(index + 1);
}

/** Kanji numeral for counts shown in headings (八つの門). */
export function countNumeral(n: number): string {
	return ["〇", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"][n] ?? String(n);
}

const STATUS: Record<string, { en: string; key: "live" | "dev" | "soon" }> = {
	稼働中: { en: "LIVE", key: "live" },
	開発中: { en: "IN DEVELOPMENT", key: "dev" },
	準備中: { en: "COMING SOON", key: "soon" },
	構想中: { en: "PLANNED", key: "soon" },
};

/** English label and style key for a lab or work status. */
export function statusInfo(status: string | null | undefined) {
	return (status && STATUS[status]) || STATUS["準備中"];
}
