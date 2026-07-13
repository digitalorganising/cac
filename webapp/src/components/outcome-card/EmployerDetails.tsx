import { ExternalLinkIcon } from "@radix-ui/react-icons";
import Link from "next/link";
import {
  companiesHouseUrl,
  getCompanyTypeFilterValue,
  getEntityTypeLabel,
} from "@/lib/company";
import {
  type AppSearchParams,
  addParamValue,
  appSearchParamsCache,
  appSearchParamsSerializer,
} from "@/lib/search-params";
import { Outcome, OutcomeCompanySic } from "@/lib/types";

type Props = {
  employer: Outcome["parties"]["employer"];
  company?: Outcome["company"];
};

const typeBadgeClass = "rounded-md px-2.5 py-0.5 inline-block bg-slate-200";
const typeBadgeLinkClass = `${typeBadgeClass} hover:bg-slate-300`;

const filterLinkClass =
  "text-primary underline underline-offset-4 hover:font-medium";

const hoverFilterLinkClass =
  "text-primary hover:underline underline-offset-4 hover:font-medium";

const sectionLinkClass =
  "font-medium text-muted-foreground hover:underline underline-offset-4 hover:text-foreground";

const descriptionListClass = "list-none mt-2 space-y-2";

const descriptionItemClass =
  "flex gap-x-1.5 leading-snug before:content-['–'] before:text-slate-400 before:shrink-0";

const groupSicsBySection = (
  sics: OutcomeCompanySic[],
): [string, OutcomeCompanySic[]][] => {
  const groups = new Map<string, OutcomeCompanySic[]>();
  for (const sic of sics) {
    const existing = groups.get(sic.section) ?? [];
    existing.push(sic);
    groups.set(sic.section, existing);
  }
  return [...groups.entries()];
};

const filterHref = (
  params: AppSearchParams,
  key: keyof AppSearchParams,
  value: string,
) => appSearchParamsSerializer(addParamValue(params, key, value));

const NatureOfBusiness = ({
  sics,
  params,
}: {
  sics: OutcomeCompanySic[];
  params: AppSearchParams;
}) => {
  if (sics.length === 0) {
    return null;
  }

  const sections = groupSicsBySection(sics);

  return (
    <ul className="list-none space-y-3.5">
      {sections.map(([section, entries]) => (
        <li key={section}>
          <Link
            href={filterHref(params, "company.sics.section", section)}
            className={sectionLinkClass}
          >
            {section}
          </Link>
          <ul className={descriptionListClass}>
            {entries.map((sic) => (
              <li key={sic.code} className={descriptionItemClass}>
                <Link
                  href={filterHref(params, "company.sics.code", sic.code)}
                  className={hoverFilterLinkClass}
                  data-sic-code={sic.code}
                >
                  {sic.description}
                </Link>
              </li>
            ))}
          </ul>
        </li>
      ))}
    </ul>
  );
};

const EmployerDetails = ({ employer, company }: Props) => {
  const params = appSearchParamsCache.all();
  const employerFilterHref = filterHref(params, "parties.employer", employer);

  if (!company) {
    return (
      <Link href={employerFilterHref} className={filterLinkClass}>
        {employer}
      </Link>
    );
  }

  const companyTypeHref = filterHref(
    params,
    "company.type",
    getCompanyTypeFilterValue(company),
  );

  return (
    <div className="flex flex-col gap-y-3">
      <Link href={employerFilterHref} className={filterLinkClass}>
        {company.name}
      </Link>
      <div>
        {company.type === "identified" && company.number ? (
          <Link
            href={companiesHouseUrl(company.number)}
            target="_blank"
            className={`${typeBadgeLinkClass} inline-flex items-center gap-x-1`}
            aria-label={`View ${company.name} on Companies House`}
          >
            Companies House
            <ExternalLinkIcon className="size-3" />
          </Link>
        ) : (
          <Link href={companyTypeHref} className={typeBadgeLinkClass}>
            {getEntityTypeLabel(company)}
          </Link>
        )}
      </div>
      {company.sics.length > 0 ? (
        <div className="xs:rounded-md xs:border xs:border-slate-200">
          <div className="xs:px-3 xs:pt-2.5 xs:pb-1 text-md font-semibold">
            Nature of business
          </div>
          <div className="xs:px-3 xs:pb-3 xs:pt-1 text-sm">
            <NatureOfBusiness sics={company.sics} params={params} />
          </div>
        </div>
      ) : null}
    </div>
  );
};

export default EmployerDetails;
