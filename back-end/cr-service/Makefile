PROJECT_ID := academic-pillar-477019-m8
REGION := europe-west1
SERVICE_NAME := plantdisease
IMAGE := $(REGION)-docker.pkg.dev/$(PROJECT_ID)/cloudrun-repo/$(SERVICE_NAME):latest

.PHONY: all build push deploy clean

all: build push deploy

build:
	docker build -t $(IMAGE) .

push:
	docker push $(IMAGE)

deploy:
	gcloud run deploy $(SERVICE_NAME) \
		--image $(IMAGE) \
		--platform managed \
		--region $(REGION) \
		--allow-unauthenticated

clean:
	docker rmi $(IMAGE)




