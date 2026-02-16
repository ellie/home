default: build

build:
    ./build.sh

serve:
    ./build.sh && zola serve

clean:
    rm -rf public content/_git-dates.json
