import { ExternalLinkIcon } from "@radix-ui/react-icons";
import Link from "next/link";
import {
  companiesHouseUrl,
  getCompanyTypeFilterValue,
  getEntityTypeLabel,
} from "@/lib/company";
import {
  addParamValue,
  appSearchParamsCache,
  appSearchParamsSerializer,
  type AppSearchParams,
} from "@/lib/search-params";
import { Outcome, OutcomeCompanySic } from "@/lib/types";
import { cn } from "@/lib/utils";

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

const descriptionListClass = "list-none mt-1 space-y-1.5";

const descriptionItemClass = "border-l border-slate-300 pl-2 leading-snug";

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

  if (sics.length === 1) {
    const sic = sics[0];
    return (
      <p>
        <Link
          href={filterHref(params, "company.sics.section", sic.section)}
          className={sectionLinkClass}
        >
          {sic.section}
        </Link>
        :{" "}
        <Link
          href={filterHref(params, "company.sics.code", sic.code)}
          className={hoverFilterLinkClass}
          data-sic-code={sic.code}
        >
          {sic.description}
        </Link>
      </p>
    );
  }

  const sections = groupSicsBySection(sics);

  if (sections.length === 1) {
    const [section, entries] = sections[0];
    return (
      <div>
        <Link
          href={filterHref(params, "company.sics.section", section)}
          className={sectionLinkClass}
        >
          {section}
        </Link>
        <ul className={descriptionListClass}>
          {entries.map((sic) => (
            <li key={sic.code}>
              <Link
                href={filterHref(params, "company.sics.code", sic.code)}
                className={cn(descriptionItemClass, hoverFilterLinkClass, "block")}
                data-sic-code={sic.code}
              >
                {sic.description}
              </Link>
            </li>
          ))}
        </ul>
      </div>
    );
  }

  return (
    <ul className="list-none space-y-2.5">
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
              <li key={sic.code}>
                <Link
                  href={filterHref(params, "company.sics.code", sic.code)}
                  className={cn(descriptionItemClass, hoverFilterLinkClass, "block")}
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
    <div className="flex flex-col gap-y-2">
      <Link href={employerFilterHref} className={filterLinkClass}>
        {company.name}
      </Link>
      <div className="pt-0.5">
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
      <NatureOfBusiness sics={company.sics} params={params} />
    </div>
  );
};

export default EmployerDetails;
