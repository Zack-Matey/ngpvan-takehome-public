import requests
import csv
import os.path

def bestVariant(variants, messageID, username, password):
    # Fetch variant details and return variant with highest opens/recipients score from a particular messageID
    highestVariant = ""
    highestVariantScore = 0
    currVariantScore = 0
    for j in range(len(variants)):
        res = requests.get("https://api.myngp.com/v2/broadcastEmails/" + str(messageID) + "/variants/" + str(variants[j]['emailMessageVariantId']) +"?$expand=statistics", auth=(username, password))
        data = res.json()
        opens = data['statistics']['opens']
        recipients = data['statistics']['recipients']
        name = data['name']
        currVariantScore = opens/recipients
        if currVariantScore > highestVariantScore:
            highestVariantScore = currVariantScore
            highestVariant = name
    return highestVariant


def emailDetails(messageID, username, password):
    # Fetch email details on a particular messageID
    # Returns array with messageID, name, recipients, opens, clicks, ubsubscribes, bounces, and the best variant as
    # determined in bestVariant()
    url = "https://api.myngp.com/v2/broadcastEmails/" + str(messageID) + "?$expand=statistics"
    response = requests.get(url, auth=(username, password))
    name = response.json()['name']
    recipients = response.json()['statistics']['recipients']
    opens = response.json()['statistics']['opens']
    clicks = response.json()['statistics']['clicks']
    ubsubs = response.json()['statistics']['unsubscribes']
    bounces = response.json()['statistics']['bounces']
    variant = bestVariant(response.json()['variants'], messageID, username, password)
    details = [messageID, name, recipients, opens, clicks, ubsubs, bounces, variant]
    return details


def main():
    # Pagination structure to accomidate > 25 emails
    # API calls and data processing
    moreEmails = True;
    while moreEmails:
        header = ["Email Message ID", "Email Name", "Recipients", "Opens", "Clicks", "Unsubscribes", "Bounces", "Top Variant"]
        csvData = []
        url = "https://api.myngp.com/v2/BroadcastEmails?$top=25"
        username = "apiuser"
        password = "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        response = requests.get(url, auth=(username, password))
        data = response.json()
        count = data['count']
        if count < 25:
            moreEmails = False
        for i in range(count):
            details = emailDetails(data['items'][i]['emailMessageId'], username, password)
            csvData.append(details)

    # User prompt if the report exists
    confirm = True
    if (os.path.isfile("EmailReport.csv")):
        invalid = True
        confirm = False
        while invalid:
            response = input("File already exists - replace file? (Y/N) ")
            if (response == "Y"):
                os.remove("EmailReport.csv")
                invalid = False
                confirm = True
            elif (response == "N"):
                print("Terminating...");
                invalid = False
                confirm = False
    
    # Write report to disk
    if confirm:
        with open('EmailReport.csv', 'w', encoding='UTF8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(sorted(csvData))
            print("Email report complete, file is EmailReport.csv")

main()