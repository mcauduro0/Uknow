import DashboardLayout from "@/components/layout/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { 
  Activity, 
  Clock, 
  FileText, 
  Zap, 
  ArrowRight, 
  MoreHorizontal,
  CheckCircle2,
  AlertCircle,
  Loader2
} from "lucide-react";
import { Link } from "wouter";

export default function Home() {
  // Mock data for dashboard
  const stats = [
    { title: "Active Research", value: "3", icon: Activity, change: "+1 from yesterday", trend: "up" },
    { title: "Completed Reports", value: "128", icon: FileText, change: "+12% this month", trend: "up" },
    { title: "Avg. Processing Time", value: "4m 12s", icon: Clock, change: "-30s improvement", trend: "up" },
    { title: "System Load", value: "24%", icon: Zap, change: "Optimal", trend: "neutral" },
  ];

  const recentTasks = [
    { id: "TASK-8921", query: "Future of Quantum Computing in Finance", status: "processing", agent: "Deep Researcher", progress: 65, time: "2m ago" },
    { id: "TASK-8920", query: "Competitor Analysis: Cloud Infrastructure 2025", status: "completed", agent: "Packager", progress: 100, time: "15m ago" },
    { id: "TASK-8919", query: "Impact of AI Regulation on SaaS Valuation", status: "completed", agent: "Packager", progress: 100, time: "1h ago" },
    { id: "TASK-8918", query: "Sustainable Energy Market Trends in SEA", status: "failed", agent: "Debate Analyst", progress: 45, time: "3h ago" },
  ];

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Hero Section */}
        <div className="relative overflow-hidden rounded-xl border border-border bg-card p-8">
          <div className="absolute inset-0 bg-[url('/images/hero-bg.png')] bg-cover bg-center opacity-20 mix-blend-overlay"></div>
          <div className="absolute inset-0 bg-gradient-to-r from-background via-background/80 to-transparent"></div>
          
          <div className="relative z-10 max-w-2xl">
            <h1 className="text-3xl font-bold tracking-tight mb-2">Investment Committee Intelligence</h1>
            <p className="text-muted-foreground mb-6 text-lg">
              Deploy multi-agent autonomous research to analyze markets, competitors, and investment opportunities with institutional depth.
            </p>
            <div className="flex gap-4">
              <Link href="/new">
                <Button size="lg" className="gap-2 shadow-lg shadow-primary/20">
                  <Zap className="w-4 h-4" />
                  Start New Research
                </Button>
              </Link>
              <Button variant="outline" size="lg" className="bg-background/50 backdrop-blur-sm">
                View Documentation
              </Button>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat, i) => (
            <Card key={i} className="border-border/50 bg-card/50 backdrop-blur-sm hover:bg-card/80 transition-colors">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.title}
                </CardTitle>
                <stat.icon className="h-4 w-4 text-primary" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold font-mono">{stat.value}</div>
                <p className="text-xs text-muted-foreground mt-1">
                  {stat.change}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Recent Activity */}
        <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Recent Research Tasks</CardTitle>
              <CardDescription>Real-time monitoring of agent activities</CardDescription>
            </div>
            <Button variant="ghost" size="sm" className="gap-1">
              View All <ArrowRight className="w-4 h-4" />
            </Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-1">
              {recentTasks.map((task) => (
                <div key={task.id} className="group flex items-center justify-between p-4 rounded-lg hover:bg-accent/50 transition-colors border border-transparent hover:border-border/50">
                  <div className="flex items-center gap-4">
                    <div className={`w-2 h-2 rounded-full ${
                      task.status === 'processing' ? 'bg-blue-500 animate-pulse' : 
                      task.status === 'completed' ? 'bg-emerald-500' : 'bg-red-500'
                    }`} />
                    <div>
                      <div className="font-medium text-sm">{task.query}</div>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground mt-1">
                        <span className="font-mono bg-accent px-1.5 py-0.5 rounded text-[10px]">{task.id}</span>
                        <span>•</span>
                        <span>{task.agent}</span>
                        <span>•</span>
                        <span>{task.time}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-6">
                    <div className="hidden md:flex flex-col items-end gap-1 min-w-[100px]">
                      <div className="flex items-center justify-between w-full text-xs text-muted-foreground">
                        <span>Progress</span>
                        <span>{task.progress}%</span>
                      </div>
                      <div className="w-full h-1.5 bg-secondary rounded-full overflow-hidden">
                        <div 
                          className={`h-full rounded-full ${
                            task.status === 'failed' ? 'bg-destructive' : 'bg-primary'
                          }`} 
                          style={{ width: `${task.progress}%` }}
                        />
                      </div>
                    </div>
                    
                    <div className="w-8 flex justify-end">
                      {task.status === 'processing' ? (
                        <Loader2 className="w-4 h-4 animate-spin text-primary" />
                      ) : task.status === 'completed' ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                      ) : (
                        <AlertCircle className="w-4 h-4 text-destructive" />
                      )}
                    </div>
                    
                    <Button variant="ghost" size="icon" className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity">
                      <MoreHorizontal className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
