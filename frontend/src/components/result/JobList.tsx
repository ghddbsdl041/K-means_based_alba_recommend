import { useEffect, useMemo, useRef, useState } from "react";
import type { Job } from "../../types/job";
import JobCard from "./JobCard";
import { getTheme } from "../../constants/clusterTheme";

interface JobListProps {
  jobs: Job[];
  clusterId: number | null;
  preferredGus: string[];
  onShowAll: () => void;
  onChangeGu: () => void;
}

function RegionDropdown({
  regions,
  selected,
  onChange,
}: {
  regions: string[];
  selected: string;
  onChange: (r: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleOutside);
    return () => document.removeEventListener("mousedown", handleOutside);
  }, []);

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen((v) => !v)}
        className={[
          "flex items-center gap-2 px-3 py-1.5 rounded-xl border text-xs font-medium transition-colors",
          open || selected !== "전체"
            ? "border-violet-400 bg-violet-50 text-violet-700"
            : "border-gray-200 bg-white/70 text-gray-500 hover:border-violet-300",
        ].join(" ")}
      >
        <span>📍 {selected}</span>
        <svg
          className={`w-3 h-3 transition-transform ${open ? "rotate-180" : ""}`}
          viewBox="0 0 12 12" fill="none"
        >
          <path d="M2 4l4 4 4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>

      {open && (
        <div className="absolute top-full right-0 mt-1.5 z-20 min-w-[140px] max-h-52 rounded-2xl border border-white/60 bg-white/90 backdrop-blur-md shadow-lg py-1.5 overflow-y-auto">
          {regions.map((r) => (
            <button
              key={r}
              onClick={() => { onChange(r); setOpen(false); }}
              className={[
                "w-full text-left px-4 py-2 text-xs transition-colors",
                selected === r
                  ? "bg-violet-100 text-violet-700 font-semibold"
                  : "text-gray-600 hover:bg-violet-50 hover:text-violet-600",
              ].join(" ")}
            >
              {r}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default function JobList({ jobs, clusterId, preferredGus, onShowAll, onChangeGu }: JobListProps) {
  const [regionFilter, setRegionFilter] = useState<string>("전체");
  const theme = getTheme(clusterId ?? 0);

  const regions = useMemo(() => {
    const set = new Set(
      jobs
        .map((j) => j.region?.split(" ")[1])
        .filter((r): r is string => Boolean(r) && r !== "전체"),
    );
    return ["전체", ...Array.from(set).sort()];
  }, [jobs]);

  const hasGuFilter = preferredGus.length > 0;

  const preferredJobs = hasGuFilter
    ? jobs.filter((j) => preferredGus.some((gu) => j.region?.includes(gu)))
    : [];
  const otherJobs = hasGuFilter
    ? jobs.filter((j) => !preferredGus.some((gu) => j.region?.includes(gu)))
    : jobs;

  const filteredOther = regionFilter === "전체"
    ? otherJobs
    : otherJobs.filter((j) => j.region?.split(" ")[1] === regionFilter);

  if (jobs.length === 0) {
    return <p className="text-center text-gray-400 py-12">추천 공고가 없습니다.</p>;
  }

  return (
    <div className="flex flex-col gap-3">
      {/* ── 내 동네 섹션 ── */}
      {hasGuFilter && preferredJobs.length > 0 && (
        <>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className={`text-sm font-semibold ${theme.summaryStrong}`}>
                📍 내 동네 공고
              </span>
              <span className={`text-xs ${theme.summaryText}`}>{preferredJobs.length}개</span>
            </div>
            <button
              onClick={onChangeGu}
              className="text-xs text-gray-400 hover:text-violet-600 underline underline-offset-2 transition-colors"
            >
              지역 변경
            </button>
          </div>

          {preferredJobs.map((job, i) => (
            <JobCard key={`preferred-${i}`} job={job} rank={i + 1} highlight />
          ))}

          {/* 그 외 섹션 구분 */}
          {otherJobs.length > 0 && (
            <div className="flex items-center gap-3 pt-2 pb-1">
              <div className="flex-1 h-px bg-gray-200" />
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-400">그 외 지역 공고</span>
                <RegionDropdown
                  regions={regions}
                  selected={regionFilter}
                  onChange={setRegionFilter}
                />
              </div>
              <div className="flex-1 h-px bg-gray-200" />
            </div>
          )}

          {filteredOther.map((job, i) => (
            <JobCard key={`other-${i}`} job={job} rank={preferredJobs.length + i + 1} />
          ))}
        </>
      )}

      {/* ── 내 동네 공고 없음 ── */}
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
            <JobCard key={`other-nogu-${i}`} job={job} rank={i + 1} />
          ))}
        </>
      )}

      {/* ── 지역 필터 없음 (전체) ── */}
      {!hasGuFilter && (
        <>
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm font-semibold text-gray-700">
              추천 공고{" "}
              <span className="text-violet-600">
                {regionFilter === "전체" ? jobs.length : filteredOther.length}개
              </span>
              {regionFilter !== "전체" && (
                <span className="text-gray-400 font-normal text-xs ml-1">/ 전체 {jobs.length}개</span>
              )}
            </span>
            <RegionDropdown
              regions={regions}
              selected={regionFilter}
              onChange={setRegionFilter}
            />
          </div>
          {filteredOther.map((job, i) => (
            <JobCard key={`all-${i}`} job={job} rank={i + 1} />
          ))}
        </>
      )}
    </div>
  );
}
