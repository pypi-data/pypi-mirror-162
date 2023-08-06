# 用于创建插件压缩包和编译镜像

VERSION?=$(shell grep '^version: ' plugin.spec.yaml | sed 's/version: //')
NAME?=$(shell grep '^name: ' plugin.spec.yaml | sed 's/name: //')
VENDOR?=$(shell grep '^vendor: ' plugin.spec.yaml | sed 's/vendor: //')
CWD?=$(shell basename $(PWD))
_NAME?=$(shell echo $(NAME) | awk '{ print toupper(substr($$0,1,1)) tolower(substr($$0,2)) }')
PKG=$(VENDOR)-$(NAME)-$(VERSION).tar.gz
IMG_PKG=$(VENDOR)-$(NAME)-$(VERSION)-offline.tar.gz
IMAGENAME="plugin.tar.gz"

.DEFAULT_GOAL := default

default: tarball

tarball:
	$(info [$(YELLOW)*$(NORMAL)] Creating plugin tarball)
	rm -rf build
	rm -rf $(PKG)
	tar -cvzf $(PKG) --exclude=$(PKG) --exclude=tests --exclude=run.sh --exclude=$(IMAGENAME) --exclude=$(IMG_PKG) *

image:
	rm -rf $(IMG_PKG) $(IMAGENAME)
	$(info [$(YELLOW)*$(NORMAL)] Building plugin image)
	docker build --pull -t $(VENDOR)/$(NAME):$(VERSION) .
	docker save -o $(IMAGENAME) $(VENDOR)/$(NAME):$(VERSION)
	tar -cvzf $(IMG_PKG) $(IMAGENAME) plugin.spec.yaml icon.png help.md
	rm -f $(IMAGENAME)



