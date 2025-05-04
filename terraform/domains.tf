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

data "aws_instances" "search" {
  instance_state_names = ["running"]
  instance_tags = {
    "aws:autoscaling:groupName" = aws_autoscaling_group.search.name
  }
}

resource "aws_route53_record" "digitalorganising_cac_api" {
  zone_id = aws_route53_zone.digitalorganising.zone_id
  name    = "search.cac.digitalorganis.ing"
  type    = "A"
  ttl     = "300"
  records = data.aws_instances.search.public_ips
}
