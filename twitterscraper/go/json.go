package main

import (
    "context"
    "encoding/json"
    "fmt"
    "os"
    "time"
    "bufio"
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

    file, err := os.Create("tweets.json")
    if err != nil {
        panic(err)
    }
    defer file.Close()

    writer := bufio.NewWriter(file)
    for tweet := range scraper.GetTweets(context.Background(), "USERNAME", 4000) {
        if tweet.Error != nil {
            panic(tweet.Error)
        }

        tweetJSON, err := json.Marshal(tweet)
        if err != nil {
            panic(err)
        }

        _, err = writer.WriteString(string(tweetJSON) + "\n")
        if err != nil {
            panic(err)
        }

        fmt.Println(string(tweetJSON))
        time.Sleep(5 * time.Second)
    }

    err = writer.Flush()
    if err != nil {
        panic(err)
    }

    fmt.Println("Tweet objects saved to tweets.json")
}
