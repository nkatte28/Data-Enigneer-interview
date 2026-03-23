# NK-specific — “Tell me about yourself” (Nike / data platform)

Use this for interviews where you want a **Nike + inventory + platform + GenAI** narrative. Tone: senior IC, technical but conversational.

---

I’m a Senior Data Engineer with over 10 years of experience building large-scale data platforms and distributed data processing systems.

For the past five years I’ve been working with Nike in the inventory and planning domain, where I design and develop data pipelines that support supply chain analytics and inventory planning across the business.

In this role, I work on integrating inventory data from multiple operational systems to create a unified view of inventory across different channels. 

For example, wholesale inventory data is sourced from SAP systems, retail store inventory events are streamed through Nike’s internal streaming platform (NSP) using Kafka, and some regional inventory feeds—such as Canada—are delivered through S3-based batch ingestion. 

My work focuses on designing pipelines that ingest, standardize, and process this data so downstream planning and analytics systems can operate on a consistent inventory dataset.

Beyond the foundational pipelines, I’ve also worked on building the analytical layer on top of this data to support planning and reporting use cases. 

Using planning data together with inventory feeds from multiple sources, 

we built curated datasets that generate key inventory KPIs such as Beginning of Period Inventory (BOP),

End of Period Inventory (EOP), sell-through rates, and weeks of supply.

These metrics are used by planning teams to monitor inventory positions and make replenishment and allocation decisions.

Alongside building new pipelines and analytical datasets, 

I also contributed to modernizing the data platform. One of the key initiatives 

I worked on was migrating ETL workloads from EMR to Databricks. I was involved across the full lifecycle—from architecture 

and data modeling to pipeline development, validation, monitoring, and performance optimization. 

As part of this effort we implemented a medallion architecture using Bronze, Silver, and Gold layers to improve data quality, maintainability, and downstream data consumption.

Prior to Nike, I worked at Florida Blue where my role focused on both data engineering and platform development. 

We developed a scalable ingestion framework using Scala and Akka to handle high volumes of incoming data from multiple source systems.

The platform was deployed on AWS using EKS with Docker and Kubernetes for containerized workloads and orchestration,

allowing ingestion pipelines to scale reliably as data volumes increased. 

I also worked extensively with enterprise data warehouses such as DB2 and Teradata to support reporting and analytics use cases.

More recently, I’ve been exploring the generative AI space as well. 

I worked on an internal automation use case where we integrated an LLM-based workflow into our CI/CD pipeline. 

We added a Jenkins stage that automatically generates technical documentation using an 

LLM API and publishes updates to Confluence based on code changes. Along with that I’ve been learning more 

about embeddings, vector databases, and retrieval-augmented generation (RAG) architectures.

Overall, I bring strong experience in building scalable data platforms and delivering 

analytics-ready datasets, while also exploring ways to enhance these systems with emerging AI capabilities.

---

## Minor edits applied (for reference)

| Change | Why |
|--------|-----|
| Em-dashes around “such as Canada” | Slightly clearer parenthetical read |
| “Scala and Akka” (dropped “the Akka framework”) | Avoids redundant “framework” after Akka |
| Em-dashes in “full lifecycle—from…” | Matches formal technical writing style |

Everything else is unchanged from your draft.
