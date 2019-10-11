//: A UIKit based Playground for presenting user interface
  
import SwiftUI
import PlaygroundSupport

struct Event {
    var eventName: String
    var eventParams: [String: Codable]
}

class Logger {
    
    private var loggingId: String?
    private let urlSession = URLSession.shared
    
    private var eventsQueue = [Event]()
    
    init() {
        getLoggingId()
    }
    
    private enum Endpoint: String {
        case client = "http://127.0.0.1:8000/api/clients/"
        case event = "http://127.0.0.1:8000/api/events/"
    }
    
    private func sendPostRequest(to endpoint: Endpoint, jsonDict: [String: Any], completion: @escaping (Data?, URLResponse?, Error?) -> Void) {
        var request = URLRequest(url: URL(string: endpoint.rawValue)!)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        let jsonData = try! JSONSerialization.data(withJSONObject: jsonDict, options: [])
        let task = urlSession.uploadTask(with: request, from: jsonData, completionHandler: completion)
        task.resume()
    }
    
    func getLoggingId() {
        let json = [
            "client_platform" : "iOS 13 SwiftUI",
            "client_version" : "1.0beta1",
        ]
        sendPostRequest(to: .client, jsonDict: json) { (data, response, error) in
            guard let data = data else { return }
            do {
                let json = try JSONSerialization.jsonObject(with: data, options: []) as! [String: Any]
                self.loggingId = json["client_hash"] as? String
                self.processQueueIfPossible()
            } catch {
                print("JSON error: \(error.localizedDescription)")
            }
        }
    }
    
    private func processQueueIfPossible() {
        guard let loggingId = loggingId else {
            print("Can't send events")
            return
        }
        
        guard let firstEvent = eventsQueue.first else {
            print("No events to be sent")
            return
        }
        
        eventsQueue.remove(at: 0)
        
        let json: [String: Any] = [
            "event_name" : firstEvent.eventName,
            "params" :firstEvent.eventParams.keys.map { ["param_name" : $0, "param_value" : firstEvent.eventParams[$0]!] },
            "client" : loggingId,
        ]
        
        sendPostRequest(to: .event,
                        jsonDict: json) { [weak self] (data, response, error) in
                            guard let data = data else {
                                self?.eventsQueue.append(firstEvent)
                                return
                            }
                            do {
                                let json = try JSONSerialization.jsonObject(with: data, options: []) as! [String: Any]
                                print("Log success: ", json)
                            } catch {
                                print("JSON error: \(error.localizedDescription)")
                            }
                            self?.processQueueIfPossible()
        }
    }
    
    func logEvent(_ eventName: String, eventParams: [String: Codable]) {
        let event = Event(eventName: eventName, eventParams: eventParams)
        eventsQueue.append(event)
        processQueueIfPossible()
    }
}

let logger = Logger()
logger.logEvent("App Start", eventParams: ["foo1" : "bar"])

struct BaseScreen: View {
    var body: some View {
        VStack {
            Button("Tap to log event 1", action: {
                logger.logEvent("Event 1", eventParams: ["foo" : "bar", "foofoo" : "baz"])
            })
            Button("Tap to log event 2", action: {
                logger.logEvent("Event 2", eventParams: ["foo" : "barbarbar", "buzz" : "bazz"])
            })
        }
    }
}


// Present the view controller in the Live View window
PlaygroundPage.current.liveView = UIHostingController(rootView: BaseScreen())
