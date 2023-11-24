# CloudVerge File Hosting Service

## Overview

This repository contains the core components of CloudVerge file hosting, designed with inspiration from the Google File System and a strong emphasis on user authorization.

CloudVerge's target is to ensure secure and efficient management of file storage and retrieval, handling heavy read/write requests seamlessly. Our architecture is composed of three main components: Client API, Balancer, and Storage. Each serves a distinct purpose in providing a reliable and scalable file hosting service.

## Architecture Overview

You can find an architecture plan on [Miro board](https://miro.com/app/board/uXjVMjYI9nM=/?share_link_id=338667676002)

### Client-API
This component is responsible for accepting user requests, verifying them, and, if successful, routing them further to balancer. On this step Postgres DB is used to manage the users security information.

### Balancer
Located between of Client-API and Storage untis, Balancer receives verified requests from users and selects an appropriate Storage unit for file writing or reading. The main goal of the balancer is to ensure the efficiency of the entire distributed system and optimal execution of heavy requests to Storage units.

### Storage
Storage handles the heavy-lifting of user read/write file requests and persists files on its hard disk storage. It's optimized to manage large volumes of data and provide quick access when needed. This component provides horizontal scaling of the entire system.

## Technologies Stack

CloudVerge utilizes the following technologies:
- **Programming Language**: Python
- **Framework**: FastAPI
- **Database**: PostgreSQL

## Repository Structure

This repository is organized into three main directories:
- `client-api`: Contains the code of Client-API component
- `balancer`: Contains the code of Balancer component
- `storage`: Contains the code of Storage unit component

## License

This project is available under the [MIT License](LICENSE.txt). The MIT License is a permissive free software license that provides limited restrictions on reuse and is compatible with many copyleft licenses.

## Contributing

We welcome contributions from the community! If you'd like to contribute, please fork the repository, make your changes, and submit a pull request.

## Getting Started

To get started with CloudVerge, please refer to the individual README.md files within each directory for detailed instructions on setting up and running each component.

## Support

If you encounter any issues or have questions regarding CloudVerge, please leave an issue on the repository, and we will (maybe) do something about it.
