import SwiftUI
import WebKit

struct ContentView: View {
    private let url: URL = URL(string: "https://adler3d.com")!

    var body: some View {
        if #available(iOS 15.0, *) {
            WebView(url: url)
                .background(.white)
                .preferredColorScheme(.light)
        } else {
            WebView(url: url)
        }
    }
}

struct WebView: UIViewRepresentable {
    var url: URL

    func makeUIView(context: Context) -> WKWebView {
        let configuration = WKWebViewConfiguration()
        configuration.limitsNavigationsToAppBoundDomains = false
        return WKWebView(frame: .zero, configuration: configuration)
    }

    func updateUIView(_ uiView: WKWebView, context: Context) {
        let request = URLRequest(url: url)
        uiView.load(request)
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
