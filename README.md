<p align="center">
  <img src="assets/hero.svg" width="100%" alt="The Acropolis at night">
</p>

<p align="center">
  <img src="assets/intro.svg" width="100%" alt="Python, APIs, GitOps, Kubernetes">
</p>

## ✨ Highlights

Deployed in 1st Advantage's GitHub:

- ☸️ **Three K3s clusters** (dev, staging, production) run entirely from git with Flux. Image automation promotes every build from branch to staging to production, with no hand-applied manifests
- 🐍 **Python apps and APIs**: a fleet of Flask and FastAPI web apps, batch processors, and integrations built on the banking core's SOAP and REST APIs and on Microsoft Graph: staff dashboards, file processing, reporting, and notifications
- 🧩 **17 repos (and counting) on one standard**: shared CI workflows, the same repo layout and agent conventions everywhere, and one deploy path from branch build to production
- 🖥️ **CI/CD dashboard** that shows every repo's builds, promotions, and what is running on each cluster in one place
- 📬 **Notifier service** on Microsoft Graph: Teams messages and email with attachments, used by the apps for alerts and reports
- 📈 **Observability**: Prometheus, Alertmanager, Grafana, Loki, and Alloy, with alerts tuned so a page means something
- 🧰 **Guardrails in CI and in the cluster**: Kyverno policies validated before they reach a cluster, secret scanning, Trivy image scans, Dependabot with grouped auto-merge, Pinniped for named-user kubectl, Entra SSO on the apps
- 🔁 **Business continuity**: an on-prem Gitea mirror of GitHub with Flux failover, and a tiered backup design across Proxmox Backup Server, etcd, and GitOps state

## 🧠 Languages & Tools

<p align="center">
  <img src="https://skillicons.dev/icons?i=python,flask,fastapi,kubernetes,docker,githubactions,git,linux,bash,prometheus,grafana,azure,nginx,vscode&perline=7" alt="tools">
</p>

## 📊 GitHub Stats

<p align="center">
  <img src="https://streak-stats.demolab.com/?user=nharonitou&theme=github-dark-blue&hide_border=true&background=0d1117" alt="streak">
</p>

## 🐍 Contribution Snake

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/nharonitou/nharonitou/output/github-snake-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/nharonitou/nharonitou/output/github-snake.svg">
  <img src="https://raw.githubusercontent.com/nharonitou/nharonitou/output/github-snake.svg" width="100%" alt="contribution snake">
</picture>
