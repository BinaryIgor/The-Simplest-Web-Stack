# FROM maven:3-eclipse-temurin-21-alpine AS build
#
# WORKDIR /build
#
# COPY src ./src
# COPY pom.xml .
#
# RUN mvn clean package

FROM eclipse-temurin:21-alpine
# COPY --from=build /build/target/the-simplest-web-stack-app-1.0-SNAPSHOT.jar /the-simplest-web-stack-app.jar
COPY target/the-simplest-web-stack-app-1.0-SNAPSHOT.jar /the-simplest-web-stack-app.jar
ENTRYPOINT exec java -jar the-simplest-web-stack-app.jar