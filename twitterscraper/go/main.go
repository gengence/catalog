package main

import (
    "context"
    "fmt"
    "os"
    "bufio"
	"time"
    twitterscraper "github.com/imperatrona/twitter-scraper"
)

func main() {
    scraper := twitterscraper.New()

    scraper.SetAuthToken(twitterscraper.AuthToken{
        Token:     "YOUR_AUTH_TOKEN", 
        CSRFToken: "YOUR_CSRF_TOKEN",
    })

    if !scraper.IsLoggedIn() {
        panic("Invalid AuthToken or not logged in")
    }

    file, err := os.Create("tweets.txt")
    if err != nil {
        panic(err)
    }
    defer file.Close()

    writer := bufio.NewWriter(file)

    for tweet := range scraper.GetTweets(context.Background(), "USERNAME", 4000) {
        if tweet.Error != nil {
            panic(tweet.Error)
        }
        _, err := writer.WriteString(tweet.Text + "\n")
        if err != nil {
            panic(err)
        }
		time.Sleep(5 * time.Second)
    }

    err = writer.Flush()
    if err != nil {
        panic(err)
    }

    fmt.Println("Tweets saved to tweets.txt")
}
