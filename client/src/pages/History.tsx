import DashboardLayout from "@/components/layout/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { 
  Search, 
  Filter, 
  Download, 
  MoreHorizontal, 
  FileText, 
  Presentation, 
  Code,
  Calendar
} from "lucide-react";

export default function History() {
  const historyItems = [
    { id: "TASK-8920", query: "Competitor Analysis: Cloud Infrastructure 2025", type: "report", date: "Oct 24, 2025", status: "Completed" },
    { id: "TASK-8919", query: "Impact of AI Regulation on SaaS Valuation", type: "slides", date: "Oct 24, 2025", status: "Completed" },
    { id: "TASK-8915", query: "Generative AI in Healthcare: Market Sizing", type: "report", date: "Oct 23, 2025", status: "Completed" },
    { id: "TASK-8912", query: "Crypto Exchange Liquidity Analysis Q3", type: "app", date: "Oct 22, 2025", status: "Completed" },
    { id: "TASK-8908", query: "EV Battery Supply Chain Vulnerabilities", type: "report", date: "Oct 21, 2025", status: "Completed" },
    { id: "TASK-8901", query: "SpaceX Starship Launch Economics", type: "slides", date: "Oct 20, 2025", status: "Completed" },
  ];

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'report': return <FileText className="w-4 h-4 text-blue-500" />;
      case 'slides': return <Presentation className="w-4 h-4 text-orange-500" />;
      case 'app': return <Code className="w-4 h-4 text-purple-500" />;
      default: return <FileText className="w-4 h-4" />;
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight mb-2">Research Archive</h1>
            <p className="text-muted-foreground text-lg">
              Access and manage past research reports and outputs.
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" className="gap-2">
              <Download className="w-4 h-4" /> Export CSV
            </Button>
          </div>
        </div>

        <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
            <div className="flex items-center gap-4 w-full max-w-md">
              <div className="relative w-full">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  type="search"
                  placeholder="Search by keyword, ID, or date..."
                  className="pl-9 bg-background/50"
                />
              </div>
              <Button variant="outline" size="icon">
                <Filter className="w-4 h-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="rounded-md border border-border">
              <div className="grid grid-cols-[1fr_3fr_1fr_1fr_1fr_auto] gap-4 p-4 border-b border-border bg-muted/30 text-xs font-medium text-muted-foreground uppercase tracking-wider">
                <div>ID</div>
                <div>Research Topic</div>
                <div>Type</div>
                <div>Date</div>
                <div>Status</div>
                <div className="w-8"></div>
              </div>
              <div className="divide-y divide-border">
                {historyItems.map((item) => (
                  <div key={item.id} className="grid grid-cols-[1fr_3fr_1fr_1fr_1fr_auto] gap-4 p-4 items-center hover:bg-accent/30 transition-colors group">
                    <div className="font-mono text-xs text-muted-foreground">{item.id}</div>
                    <div className="font-medium text-sm truncate pr-4">{item.query}</div>
                    <div className="flex items-center gap-2 text-sm capitalize">
                      {getTypeIcon(item.type)}
                      {item.type}
                    </div>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Calendar className="w-3 h-3" />
                      {item.date}
                    </div>
                    <div>
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-500">
                        {item.status}
                      </span>
                    </div>
                    <div className="w-8 flex justify-end">
                      <Button variant="ghost" size="icon" className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity">
                        <MoreHorizontal className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="flex items-center justify-center pt-6">
              <Button variant="ghost" size="sm" className="text-muted-foreground">
                Load More Results
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
