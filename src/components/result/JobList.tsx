import type { Job } from "../../types/job";
import JobCard from "./JobCard";

interface JobListProps {
  jobs: Job[];
  preferredGus: string[];
  onShowAll: () => void;
  onChangeGu: () => void;
}

export default function JobList({ jobs, preferredGus, onShowAll, onChangeGu }: JobListProps) {
  const hasGuFilter = preferredGus.length > 0;

  const preferredJobs = hasGuFilter
    ? jobs.filter((j) => preferredGus.some((gu) => j.region?.includes(gu)))
    : [];
  const otherJobs = hasGuFilter
    ? jobs.filter((j) => !preferredGus.some((gu) => j.region?.includes(gu)))
    : jobs;

  if (jobs.length === 0) {
    return <p className="text-center text-gray-400 py-12">추천 공고가 없습니다.</p>;
  }

  return (
    <div className="flex flex-col gap-4">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <h3 className="text-base font-semibold text-gray-700">
          추천 공고{" "}
          <span className="text-violet-600">
            {hasGuFilter ? preferredJobs.length : jobs.length}개
          </span>
          {hasGuFilter && (
            <span className="text-gray-400 font-normal text-sm ml-1">
              / 전체 {jobs.length}개
            </span>
          )}
        </h3>
        {hasGuFilter && (
          <button
            onClick={onChangeGu}
            className="text-xs text-violet-500 hover:text-violet-700 underline underline-offset-2 transition-colors"
          >
            📍 지역 변경
          </button>
        )}
      </div>

      {/* 내 동네 공고가 있는 경우 */}
      {hasGuFilter && preferredJobs.length > 0 && (
        <>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-violet-600 bg-violet-50 px-2.5 py-1 rounded-full">
              📍 내 동네 공고 {preferredJobs.length}개
            </span>
          </div>
          {preferredJobs.map((job, i) => (
            <JobCard key={`preferred-${job.detail_url}-${i}`} job={job} />
          ))}

          {otherJobs.length > 0 && (
            <>
              <div className="flex items-center gap-3 my-1">
                <div className="flex-1 h-px bg-gray-200" />
                <span className="text-xs text-gray-400">그 외 지역 공고</span>
                <div className="flex-1 h-px bg-gray-200" />
              </div>
              {otherJobs.map((job, i) => (
                <JobCard key={`other-${job.detail_url}-${i}`} job={job} />
              ))}
            </>
          )}
        </>
      )}

      {/* 내 동네 공고가 없는 경우 */}
      {hasGuFilter && preferredJobs.length === 0 && (
        <>
          <div className="rounded-2xl border border-amber-200 bg-amber-50 px-5 py-4 flex flex-col gap-3">
            <p className="text-sm text-amber-700 font-medium">
              선택한 지역({preferredGus.join(", ")})에 추천 공고가 없어요
            </p>
            <div className="flex gap-2">
              <button
                onClick={onShowAll}
                className="px-4 py-2 rounded-xl bg-violet-600 text-white text-xs font-medium hover:bg-violet-700 transition-colors"
              >
                전체 공고 보기
              </button>
              <button
                onClick={onChangeGu}
                className="px-4 py-2 rounded-xl border border-violet-300 text-violet-600 text-xs font-medium hover:bg-violet-50 transition-colors"
              >
                지역 다시 선택
              </button>
            </div>
          </div>
          {otherJobs.map((job, i) => (
            <JobCard key={`other-${job.detail_url}-${i}`} job={job} />
          ))}
        </>
      )}

      {/* 필터 없는 경우 */}
      {!hasGuFilter &&
        otherJobs.map((job, i) => (
          <JobCard key={`${job.detail_url}-${i}`} job={job} />
        ))}
    </div>
  );
}
