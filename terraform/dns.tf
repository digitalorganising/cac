resource "aws_route53_zone" "digitalorganising" {
  name = "digitalorganis.ing"
}

resource "aws_route53_record" "digitalorganising_apex_a" {
  zone_id = aws_route53_zone.digitalorganising.zone_id
  name    = "digitalorganis.ing"
  type    = "A"
  ttl     = "600"
  records = ["185.199.108.153", "185.199.109.153", "185.199.110.153", "185.199.111.153"]
}

resource "aws_route53_record" "digitalorganising_apex_aaaa" {
  zone_id = aws_route53_zone.digitalorganising.zone_id
  name    = "digitalorganis.ing"
  type    = "AAAA"
  ttl     = "600"
  records = ["2606:50c0:8000::153", "2606:50c0:8001::153", "2606:50c0:8002::153", "2606:50c0:8003::153"]
}

resource "aws_route53_record" "digitalorganising_www" {
  zone_id = aws_route53_zone.digitalorganising.zone_id
  name    = "www.digitalorganis.ing"
  type    = "CNAME"
  ttl     = "600"
  records = ["digitalorganising.github.io."]
}

resource "aws_route53_record" "digitalorganising_cac" {
  zone_id = aws_route53_zone.digitalorganising.zone_id
  name    = "cac.digitalorganis.ing"
  type    = "CNAME"
  ttl     = "600"
  records = ["cname.vercel-dns.com."]
}

resource "aws_route53_record" "digitalorganising_githubpages_challenge" {
  zone_id = aws_route53_zone.digitalorganising.zone_id
  name    = "_github-pages-challenge-digitalorganising.digitalorganis.ing"
  type    = "TXT"
  ttl     = "600"
  records = ["2acdd2a9081e8e711cc2417cdd90ae"]
}

resource "aws_route53_record" "cac_search" {
  zone_id = aws_route53_zone.digitalorganising.zone_id
  name    = local.endpoint
  type    = "CNAME"
  ttl     = "600"
  records = [aws_opensearch_domain.cac_search.endpoint_v2]
}

resource "aws_route53_record" "cac_search_validation" {
  for_each = {
    for dvo in aws_acm_certificate.cac_search.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = aws_route53_zone.digitalorganising.zone_id
}
