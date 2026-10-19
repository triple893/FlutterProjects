export function formatDate(date: Date | null | undefined): string {
	if (!date) return "";
	return date.toLocaleDateString("ja-JP", { year: "numeric", month: "long", day: "numeric" });
}

/** Sort entries by their `sort_order` field, falling back to the end of the list. */
export function bySortOrder<T extends { data: { sort_order?: number | null } }>(a: T, b: T): number {
	return (a.data.sort_order ?? 1000) - (b.data.sort_order ?? 1000);
}
