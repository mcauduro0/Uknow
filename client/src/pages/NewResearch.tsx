import DashboardLayout from "@/components/layout/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { 
  UploadCloud, 
  Zap, 
  FileText, 
  Presentation, 
  Code, 
  Search,
  ArrowRight
} from "lucide-react";
import { useState } from "react";
import { useLocation } from "wouter";

export default function NewResearch() {
  const [_, setLocation] = useLocation();
  const [isLoading, setIsLoading] = useState(false);
  const [outputFormat, setOutputFormat] = useState("report");
  const [quickMode, setQuickMode] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      setLocation("/");
    }, 1500);
  };

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">New Research Task</h1>
          <p className="text-muted-foreground text-lg">
            Initialize a new multi-agent research session.
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-[2fr_1fr]">
          <div className="space-y-8">
            <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle>Research Parameters</CardTitle>
                <CardDescription>Define the scope and objectives of the analysis</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="space-y-2">
                    <Label htmlFor="query">Research Question / Topic</Label>
                    <Textarea 
                      id="query" 
                      placeholder="e.g., Analyze the competitive landscape of quantum computing startups in Europe..." 
                      className="min-h-[120px] bg-background/50 resize-none font-medium"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Context Files (Optional)</Label>
                    <div className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:bg-accent/50 transition-colors cursor-pointer group">
                      <div className="w-10 h-10 bg-accent rounded-full flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform">
                        <UploadCloud className="w-5 h-5 text-muted-foreground" />
                      </div>
                      <p className="text-sm font-medium">Click to upload or drag and drop</p>
                      <p className="text-xs text-muted-foreground mt-1">PDF, DOCX, or TXT (max 10MB)</p>
                    </div>
                  </div>

                  <div className="pt-4">
                    <Button type="submit" size="lg" className="w-full gap-2" disabled={isLoading}>
                      {isLoading ? (
                        <>Processing Request...</>
                      ) : (
                        <>
                          Initialize Agents <ArrowRight className="w-4 h-4" />
                        </>
                      )}
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </div>

          <div className="space-y-6">
            <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-base">Configuration</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-3">
                  <Label>Output Format</Label>
                  <div className="grid grid-cols-3 gap-2">
                    <button 
                      type="button"
                      onClick={() => setOutputFormat("report")}
                      className={`flex flex-col items-center justify-center gap-2 p-3 rounded-lg border transition-all ${
                        outputFormat === "report" 
                          ? "bg-primary/10 border-primary text-primary" 
                          : "bg-background border-border hover:bg-accent hover:text-accent-foreground"
                      }`}
                    >
                      <FileText className="w-5 h-5" />
                      <span className="text-xs font-medium">Report</span>
                    </button>
                    <button 
                      type="button"
                      onClick={() => setOutputFormat("slides")}
                      className={`flex flex-col items-center justify-center gap-2 p-3 rounded-lg border transition-all ${
                        outputFormat === "slides" 
                          ? "bg-primary/10 border-primary text-primary" 
                          : "bg-background border-border hover:bg-accent hover:text-accent-foreground"
                      }`}
                    >
                      <Presentation className="w-5 h-5" />
                      <span className="text-xs font-medium">Slides</span>
                    </button>
                    <button 
                      type="button"
                      onClick={() => setOutputFormat("app")}
                      className={`flex flex-col items-center justify-center gap-2 p-3 rounded-lg border transition-all ${
                        outputFormat === "app" 
                          ? "bg-primary/10 border-primary text-primary" 
                          : "bg-background border-border hover:bg-accent hover:text-accent-foreground"
                      }`}
                    >
                      <Code className="w-5 h-5" />
                      <span className="text-xs font-medium">App Spec</span>
                    </button>
                  </div>
                </div>

                <div className="flex items-center justify-between p-3 rounded-lg border border-border bg-background/50">
                  <div className="space-y-0.5">
                    <Label className="text-base">Quick Mode</Label>
                    <p className="text-xs text-muted-foreground">Skip 2nd debate round</p>
                  </div>
                  <Switch checked={quickMode} onCheckedChange={setQuickMode} />
                </div>

                <div className="bg-accent/30 rounded-lg p-4 text-xs text-muted-foreground space-y-2">
                  <div className="flex items-center gap-2">
                    <Zap className="w-3 h-3 text-amber-500" />
                    <span>Est. Cost: ~0.15 USD</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Search className="w-3 h-3 text-blue-500" />
                    <span>Deep Research: Enabled</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <div className="relative overflow-hidden rounded-xl border border-border bg-card p-6">
              <div className="absolute inset-0 bg-[url('/images/analysis-card-bg.png')] bg-cover bg-center opacity-10"></div>
              <div className="relative z-10">
                <h3 className="font-semibold mb-2">Pro Tip</h3>
                <p className="text-sm text-muted-foreground">
                  Upload annual reports or 10-K filings to get specific financial analysis combined with market sentiment.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
