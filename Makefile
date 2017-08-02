project := latexbot
service := bot

registry := registry.camderwin.us
tag := $(shell echo "latest")
image := $(registry)/$(project):$(tag)

run:
	docker-compose run $(service)

bash:
	docker-compose run $(service) sh

deploy:
	docker build . -t $(image)  && \
	docker push $(image)
