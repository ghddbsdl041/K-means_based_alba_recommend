import type { Job } from "../../types/job";

interface JobCardProps {
  job: Job;
}

export default function JobCard({ job }: JobCardProps) {
  const tags = job.category
    ? job.category.split(",").map((t) => t.trim()).filter(Boolean)
    : [];

  return (
    <div className="w-full rounded-2xl border border-white/40 bg-white/60 backdrop-blur-sm p-5 hover:shadow-md hover:border-violet-200 transition-all duration-200">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-sm font-medium text-gray-500 truncate">{job.company_name}</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-violet-100 text-violet-600 shrink-0">
              {job.cluster_name}
            </span>
          </div>

          <h3 className="text-base font-semibold text-gray-900 mb-3 leading-snug line-clamp-2">
            {job.title}
          </h3>

          <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-gray-600 mb-3">
            <span>💰 {job.pay_info}</span>
            <span>⏰ {job.work_time}</span>
            <span>📍 {job.region}</span>
          </div>

          {tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {tags.slice(0, 4).map((tag) => (
                <span
                  key={tag}
                  className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-500"
                >
                  #{tag}
                </span>
              ))}
            </div>
          )}
        </div>

        <a
          href={job.detail_url}
          target="_blank"
          rel="noopener noreferrer"
          className="shrink-0 px-4 py-2 rounded-xl bg-violet-600 text-white text-sm font-medium hover:bg-violet-700 transition-colors self-center"
        >
          공고 보기 →
        </a>
      </div>
    </div>
  );
}
