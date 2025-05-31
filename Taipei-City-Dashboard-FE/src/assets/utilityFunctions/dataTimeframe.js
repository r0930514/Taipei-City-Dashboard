/* eslint-disable indent */
export function getComponentDataTimeframe(time_from, time_to, api) {
	const tzoffset = new Date().getTimezoneOffset() * 60000;
	const nowTimeFrom = new Date(Date.now());
	const nowTimeTo = new Date(Date.now());
	let parsedTimeFrom = "";
	let parsedTimeTo = "";

	if (time_from === "max") {
		nowTimeFrom.setFullYear(nowTimeFrom.getFullYear() - 30);
	} else if (time_from.split("_")[1] === "start") {
		switch (time_from.split("_")[0]) {
			case "day":
				nowTimeFrom.setHours(0, 0, 0, 0);
				break;
			case "week":
				nowTimeFrom.setHours(0, 0, 0, 0);
				nowTimeFrom.setDate(
					nowTimeFrom.getDate() - nowTimeFrom.getDay() + 1
				);
				break;
			case "month":
				nowTimeFrom.setHours(0, 0, 0, 0);
				nowTimeFrom.setDate(1);
				break;
			case "year":
				nowTimeFrom.setHours(0, 0, 0, 0);
				nowTimeFrom.setMonth(0, 1);
				break;
			default:
				break;
		}
	} else if (time_from.split("_")[1] === "ago") {
		switch (time_from.split("_")[0]) {
			case "day":
				nowTimeFrom.setDate(nowTimeFrom.getDate() - 1);
				break;
			case "week":
				nowTimeFrom.setDate(nowTimeFrom.getDate() - 7);
				break;
			case "month":
				nowTimeFrom.setMonth(nowTimeFrom.getMonth() - 1);
				break;
			case "quarter":
				nowTimeFrom.setMonth(nowTimeFrom.getMonth() - 3);
				break;
			case "halfyear":
				nowTimeFrom.setMonth(nowTimeFrom.getMonth() - 6);
				break;
			case "year":
				nowTimeFrom.setFullYear(nowTimeFrom.getFullYear() - 1);
				break;
			case "twoyear":
				nowTimeFrom.setFullYear(nowTimeFrom.getFullYear() - 2);
				break;
			case "fiveyear":
				nowTimeFrom.setFullYear(nowTimeFrom.getFullYear() - 5);
				break;
			case "tenyear":
				nowTimeFrom.setFullYear(nowTimeFrom.getFullYear() - 10);
				break;
			default:
				break;
		}
	}

	parsedTimeFrom = new Date(nowTimeFrom - tzoffset)
		.toISOString()
		.split(".")[0]
		.replace("T", " ");

	if (time_to === "now" || !time_to || time_to === "") {
		// let parsedTimeTo be the current time formated YYYY-MM-DD HH:MM:SS and in UTC+8
		parsedTimeTo = new Date(nowTimeTo - tzoffset)
			.toISOString()
			.split(".")[0]
			.replace("T", " ");
	} else {
		// 如果 time_to 是具體的時間值，嘗試解析它
		try {
			const toTime = new Date(time_to);
			if (!isNaN(toTime.getTime())) {
				parsedTimeTo = new Date(toTime - tzoffset)
					.toISOString()
					.split(".")[0]
					.replace("T", " ");
			} else {
				// 如果解析失敗，使用當前時間
				parsedTimeTo = new Date(nowTimeTo - tzoffset)
					.toISOString()
					.split(".")[0]
					.replace("T", " ");
			}
		} catch {
			// 如果發生錯誤，使用當前時間
			parsedTimeTo = new Date(nowTimeTo - tzoffset)
				.toISOString()
				.split(".")[0]
				.replace("T", " ");
		}
	}

	if (api === true) {
		return {
			timefrom: parsedTimeFrom.replace(" ", "T") + "+08:00",
			timeto: parsedTimeTo.replace(" ", "T") + "+08:00",
		};
	} else {
		return { parsedTimeFrom, parsedTimeTo };
	}
}
