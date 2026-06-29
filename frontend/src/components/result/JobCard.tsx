import type { Job } from "../../types/job";
import { getTheme } from "../../constants/clusterTheme";

interface JobCardProps {
  job: Job;
  rank?: number;
  highlight?: boolean;
}

export default function JobCard({ job, rank, highlight = false }: JobCardProps) {
  const tags = job.category
    ? job.category.split(",").map((t) => t.trim()).filter(Boolean)
    : [];

  const regionShort = job.region?.split(" ").slice(1).join(" ") ?? job.region;
  const theme = getTheme(job.cluster_id);

  return (
    <div
      className={[
        "group rounded-2xl overflow-hidden transition-all duration-200",
        "hover:-translate-y-0.5 hover:shadow-lg",
        highlight
          ? `shadow-sm border ${theme.highlightBorder} ${theme.highlightCard} backdrop-blur-sm`
          : "border border-white/50 shadow-sm bg-white/65 backdrop-blur-sm",
      ].join(" ")}
    >
      <div className="px-5 py-4">
        {/* 회사명 + 순위 */}
        <div className="flex items-center gap-2 mb-1.5">
          {rank !== undefined && (
            <span className={`text-xs font-bold tabular-nums w-5 shrink-0 ${highlight ? theme.summaryText : "text-gray-300"}`}>
              {String(rank).padStart(2, "0")}
            </span>
          )}
          <span className="text-xs text-gray-400 truncate">{job.company_name}</span>
        </div>

        {/* 공고 제목 */}
        <h3 className={[
          "text-[15px] font-semibold leading-snug line-clamp-2 mb-2.5 transition-colors",
          highlight ? `${theme.name} group-hover:opacity-80` : "text-gray-900 group-hover:text-gray-700",
        ].join(" ")}>
          {job.title}
        </h3>

        {/* 위치 · 근무시간 · 급여 */}
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-gray-500 mb-3">
          <span>📍 {regionShort}</span>
          <span className="text-gray-300">·</span>
          <span>{job.work_time}</span>
          <span className="text-gray-300">·</span>
          <span className="font-medium text-gray-700">{job.pay_info}</span>
        </div>

        {/* 태그 + CTA */}
        <div className="flex items-end justify-between gap-3">
          <div className="flex flex-wrap gap-1.5">
            {tags.slice(0, 3).map((tag) => (
              <span
                key={tag}
                className={[
                  "text-xs px-2.5 py-0.5 rounded-full font-medium",
                  highlight ? theme.highlightTag : "bg-gray-100 text-gray-500",
                ].join(" ")}
              >
                {tag}
              </span>
            ))}
          </div>

          <a
            href={job.detail_url}
            target="_blank"
            rel="noopener noreferrer"
            className={`shrink-0 px-4 py-2 rounded-xl text-sm font-semibold text-white shadow-sm transition-all duration-200 hover:shadow-md active:scale-95 ${theme.button}`}
          >
            공고 보기 →
          </a>
        </div>
      </div>
    </div>
  );
}
